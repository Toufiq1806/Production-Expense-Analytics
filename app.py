from flask import Flask, request ,jsonify
from flask_cors import CORS
import pandas as pd
import pymysql
import os
import io

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "sql123",        
    "database": "BoomTown",
}

UPLOAD_FOLDER = "PROCESSED_DATA"
COMBINED_FOLDER = "Combined_Record"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMBINED_FOLDER, exist_ok=True)

REQUIRED_COLS = {
    "catering":  {"Date", "Vendor", "Meal_Type", "Headcount", "Price_Per_Head"},
    "camera":    {"Date", "Item_Name", "Daily_Rate", "Days", "Total_Cost"},
    "transport": {"Date", "Vehicle_Type", "Fuel_AED", "Salik_Tolls", "Driver_OT_Hours"},
    "talent":    {"Actor_Name", "Role", "Agency", "Contract_Fee", "Status"},
}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BoomTown Expense Pipeline</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; padding: 40px 20px; }
  .container { max-width: 780px; margin: 0 auto; }
  h1 { font-size: 24px; font-weight: 600; color: #f8fafc; margin-bottom: 6px; }
  .subtitle { font-size: 14px; color: #94a3b8; margin-bottom: 32px; }
  .steps { display: flex; align-items: center; gap: 0; margin-bottom: 32px; }
  .step { display: flex; align-items: center; gap: 8px; }
  .step-num { width: 28px; height: 28px; border-radius: 50%; background: #1e293b; color: #64748b; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; flex-shrink: 0; transition: all 0.3s; }
  .step-num.active { background: #3b82f6; color: white; }
  .step-num.done { background: #22c55e; color: white; }
  .step-label { font-size: 13px; color: #64748b; white-space: nowrap; }
  .step-label.active { color: #f1f5f9; font-weight: 500; }
  .step-line { flex: 1; height: 1px; background: #1e293b; margin: 0 10px; min-width: 20px; transition: background 0.3s; }
  .step-line.done { background: #22c55e; }
  .card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
  .card h2 { font-size: 16px; font-weight: 600; color: #f1f5f9; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
  .dropzone { background: #0f1420; border: 1.5px dashed #374151; border-radius: 10px; padding: 18px; cursor: pointer; transition: all 0.2s; text-align: center; }
  .dropzone:hover { border-color: #3b82f6; background: #0f1929; }
  .dropzone.has-file { border-color: #22c55e; background: #0a1f10; border-style: solid; }
  .dropzone input { display: none; }
  .dropzone-icon { font-size: 24px; margin-bottom: 6px; }
  .dropzone-label { font-size: 14px; font-weight: 500; color: #e2e8f0; margin-bottom: 4px; }
  .dropzone-hint { font-size: 12px; color: #64748b; }
  .dropzone-file { font-size: 12px; color: #22c55e; margin-top: 4px; }
  .btn { background: #3b82f6; color: white; border: none; padding: 10px 22px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
  .btn:hover { background: #2563eb; }
  .btn:disabled { background: #1e293b; color: #475569; cursor: not-allowed; }
  .btn-success { background: #16a34a; }
  .btn-success:hover { background: #15803d; }
  .status-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #1e293b; }
  .status-row:last-child { border-bottom: none; }
  .badge { font-size: 11px; padding: 3px 8px; border-radius: 6px; font-weight: 600; }
  .badge-ok { background: #14532d; color: #86efac; }
  .badge-error { background: #450a0a; color: #fca5a5; }
  .dept-name { flex: 1; font-size: 14px; font-weight: 500; }
  .row-count { font-size: 12px; color: #64748b; }
  .error-msg { font-size: 12px; color: #f87171; }
  .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .metric { background: #0f1420; border-radius: 8px; padding: 14px; }
  .metric-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
  .metric-value { font-size: 20px; font-weight: 600; color: #f1f5f9; }
  .chart-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .chart-dept { font-size: 13px; width: 80px; color: #94a3b8; }
  .chart-bar-bg { flex: 1; background: #1e293b; border-radius: 4px; height: 22px; overflow: hidden; }
  .chart-bar-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; display: flex; align-items: center; padding-left: 8px; }
  .chart-bar-fill span { font-size: 11px; color: white; font-weight: 500; white-space: nowrap; }
  .success-box { background: #052e16; border: 1px solid #16a34a; border-radius: 10px; padding: 20px; display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
  .success-title { font-size: 16px; font-weight: 600; color: #86efac; }
  .success-sub { font-size: 13px; color: #4ade80; margin-top: 2px; }
  .schema-box { background: #0f1420; border-radius: 8px; padding: 14px; font-family: 'Courier New', monospace; font-size: 13px; color: #7dd3fc; line-height: 2; }
  .alert-error { background: #2d0a0a; border: 1px solid #dc2626; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #f87171; margin-bottom: 16px; }
  .hidden { display: none; }
</style>
</head>
<body>
<div class="container">
  <h1>BoomTown Expense Pipeline</h1>
  <p class="subtitle">Upload raw field data &rarr; validate &rarr; combine &rarr; push to MySQL</p>

  <div class="steps">
    <div class="step">
      <div class="step-num active" id="sn1">1</div>
      <span class="step-label active" id="sl1">Upload</span>
    </div>
    <div class="step-line" id="line1"></div>
    <div class="step">
      <div class="step-num" id="sn2">2</div>
      <span class="step-label" id="sl2">Validate</span>
    </div>
    <div class="step-line" id="line2"></div>
    <div class="step">
      <div class="step-num" id="sn3">3</div>
      <span class="step-label" id="sl3">Combine</span>
    </div>
    <div class="step-line" id="line3"></div>
    <div class="step">
      <div class="step-num" id="sn4">4</div>
      <span class="step-label" id="sl4">Push to DB</span>
    </div>
  </div>

  <div id="errorBox" class="alert-error hidden"></div>

  <div id="step1" class="card">
    <h2>Upload Department CSVs</h2>
    <div class="grid">
      <div class="dropzone" id="dz-catering" onclick="document.getElementById('f-catering').click()">
        <input type="file" id="f-catering" accept=".csv" onchange="fileSelected('catering', this)">
        <div class="dropzone-label">Catering</div>
        <div class="dropzone-hint" id="hint-catering">catering_log.csv</div>
        <div class="dropzone-file hidden" id="fname-catering"></div>
      </div>
      <div class="dropzone" id="dz-camera" onclick="document.getElementById('f-camera').click()">
        <input type="file" id="f-camera" accept=".csv" onchange="fileSelected('camera', this)">
        <div class="dropzone-label">Camera</div>
        <div class="dropzone-hint" id="hint-camera">camera_dept.csv</div>
        <div class="dropzone-file hidden" id="fname-camera"></div>
      </div>
      <div class="dropzone" id="dz-transport" onclick="document.getElementById('f-transport').click()">
        <input type="file" id="f-transport" accept=".csv" onchange="fileSelected('transport', this)">
        <div class="dropzone-label">Transport</div>
        <div class="dropzone-hint" id="hint-transport">transport_dubai.csv</div>
        <div class="dropzone-file hidden" id="fname-transport"></div>
      </div>
      <div class="dropzone" id="dz-talent" onclick="document.getElementById('f-talent').click()">
        <input type="file" id="f-talent" accept=".csv" onchange="fileSelected('talent', this)">
        <div class="dropzone-label">Talent</div>
        <div class="dropzone-hint" id="hint-talent">talent_payouts.csv</div>
        <div class="dropzone-file hidden" id="fname-talent"></div>
      </div>
    </div>
    <button class="btn" id="btnValidate" onclick="validateFiles()" disabled>Validate Files</button>
    <span id="uploadHint" style="font-size:12px;color:#64748b;margin-left:12px;">Upload all 4 files to continue</span>
  </div>

  <div id="step2" class="card hidden">
    <h2>Validation Results</h2>
    <div id="validationRows"></div>
    <br>
    <button class="btn" id="btnCombine" onclick="combineFiles()">Combine Departments</button>
  </div>

  <div id="step3" class="card hidden">
    <h2>Financial Intelligence Dashboard</h2>
    
    <!-- Modern Metric Grid -->
    <div class="metrics">
        <div class="metric">
            <div class="metric-label">Total Burn</div>
            <div class="metric-value" id="mTotal" style="color:#60a5fa">AED 0</div>
        </div>
        <div class="metric">
            <div class="metric-label">Avg Transaction</div>
            <div class="metric-value" id="mAvg">AED 0</div>
        </div>
        <div class="metric">
            <div class="metric-label">Biggest Driver</div>
            <div class="metric-value" id="mTopDept" style="color:#fbbf24">-</div>
        </div>
    </div>

    <!-- Visual Chart -->
    <div id="chartArea" style="margin-bottom:25px;"></div>

    <!-- AI Insight Box -->
    <div id="aiInsight" style="background:rgba(59, 130, 246, 0.1); border-left:4px solid #3b82f6; padding:15px; border-radius:4px; font-size:14px;">
        <strong>💡 Observation:</strong> <span id="insightText">Processing data trends...</span>
    </div>
    
    <br>
    <button class="btn btn-success" id="btnDB" onclick="pushToDB()">Finalize & Push to MySQL</button>
</div>
    <div id="chartArea" style="margin-bottom:20px;"></div>
    <button class="btn btn-success" id="btnDB" onclick="pushToDB()">Push to MySQL</button>
  </div>

  <div id="step4" class="card hidden">
    <div class="success-box">
      <div>
        <div class="success-title">Pipeline Complete!</div>
        <div class="success-sub" id="insertedMsg">Records inserted into BoomTown.expenses</div>
      </div>
    </div>
    <div class="schema-box">
      BoomTown.expenses<br>
      &nbsp;&nbsp;project_id &nbsp;&nbsp;&nbsp;INT<br>
      &nbsp;&nbsp;department &nbsp;&nbsp;VARCHAR(50)<br>
      &nbsp;&nbsp;amount &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DECIMAL(12,2)<br>
      &nbsp;&nbsp;expense_date DATE
    </div>
    <br>
    <button class="btn" onclick="location.reload()">Run Another Batch</button>
  </div>
</div>

<script>
  var depts = ['catering','camera','transport','talent'];
  var uploadedFiles = {};
  var BAR_COLORS = { catering:'#3b82f6', camera:'#f59e0b', transport:'#10b981', talent:'#ec4899' };

  function fileSelected(dept, input) {
    if (!input.files[0]) return;
    uploadedFiles[dept] = input.files[0];
    document.getElementById('dz-' + dept).classList.add('has-file');
    document.getElementById('hint-' + dept).classList.add('hidden');
    var fn = document.getElementById('fname-' + dept);
    fn.textContent = 'Selected: ' + input.files[0].name;
    fn.classList.remove('hidden');
    var allUploaded = depts.every(function(d) { return uploadedFiles[d]; });
    document.getElementById('btnValidate').disabled = !allUploaded;
    if (allUploaded) document.getElementById('uploadHint').style.display = 'none';
  }

  function showError(msg) {
    var b = document.getElementById('errorBox');
    b.textContent = 'Error: ' + msg;
    b.classList.remove('hidden');
    setTimeout(function() { b.classList.add('hidden'); }, 8000);
  }

  function setStep(n) {
    for (var i = 1; i <= 4; i++) {
      var num = document.getElementById('sn' + i);
      var lbl = document.getElementById('sl' + i);
      if (i < n) { num.className = 'step-num done'; num.textContent = 'done'; }
      else if (i === n) { num.className = 'step-num active'; num.textContent = i; lbl.className = 'step-label active'; }
      else { num.className = 'step-num'; num.textContent = i; lbl.className = 'step-label'; }
      if (i < 4) { document.getElementById('line' + i).className = 'step-line' + (i < n ? ' done' : ''); }
    }
  }

  function validateFiles() {
    var btn = document.getElementById('btnValidate');
    btn.disabled = true; btn.textContent = 'Validating...';
    var form = new FormData();
    depts.forEach(function(d) { form.append(d, uploadedFiles[d]); });
    fetch('/api/validate', { method: 'POST', body: form })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        var results = data.results;
        var html = depts.map(function(d) {
          var r = results[d];
          var ok = r.status === 'ok';
          return '<div class="status-row">' +
            '<span class="dept-name">' + d.charAt(0).toUpperCase() + d.slice(1) + '</span>' +
            '<span class="row-count">' + (r.rows ? r.rows + ' rows' : '') + '</span>' +
            '<span class="badge ' + (ok ? 'badge-ok' : 'badge-error') + '">' + (ok ? 'OK' : 'ERROR') + '</span>' +
            (!ok ? '<span class="error-msg">' + r.message + '</span>' : '') +
            '</div>';
        }).join('');
        document.getElementById('validationRows').innerHTML = html;
        document.getElementById('step2').classList.remove('hidden');
        setStep(2);
        if (!data.ready_to_combine) {
          document.getElementById('btnCombine').disabled = true;
          showError('Fix the column errors above and re-upload.');
        }
        btn.disabled = false; btn.textContent = 'Validate Files';
      })
      .catch(function(e) { showError('Validation failed: ' + e.message); btn.disabled = false; btn.textContent = 'Validate Files'; });
  }

  function combineFiles() {
    var btn = document.getElementById('btnCombine');
    btn.disabled = true;
    
    fetch('/api/combine', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.status !== 'ok') { showError(data.message); return; }

        // 1. Fill the Metric Cards
        document.getElementById('mTotal').textContent = 'AED ' + data.total_aed.toLocaleString();
        document.getElementById('mAvg').textContent = 'AED ' + data.average_spend.toLocaleString();
        document.getElementById('mTopDept').textContent = data.top_dept.toUpperCase();

        // 2. Generate Dynamic Insight Text
        let insight = `The ${data.top_dept} department accounts for ${data.concentration}% of all costs in this batch. `;
        insight += data.concentration > 50 ? "Consider reviewing vendor contracts for this department to optimize burn." : "Spending is healthy and distributed across the crew.";
        document.getElementById('insightText').textContent = insight;

        // 3. Render the Visual Bars
        var chartHTML = data.summary.map(function(s) {
            var pct = Math.round((s.total / data.total_aed) * 100);
            var color = BAR_COLORS[s.department] || '#6b7280';
            return `
                <div class="chart-bar-row">
                    <span class="chart-dept">${s.department} <small style="color:#64748b">${pct}%</small></span>
                    <div class="chart-bar-bg">
                        <div class="chart-bar-fill" style="width:${pct}%; background:${color}">
                            <span>AED ${s.total.toLocaleString()}</span>
                        </div>
                    </div>
                </div>`;
        }).join('');

        document.getElementById('chartArea').innerHTML = chartHTML;
        document.getElementById('step3').classList.remove('hidden');
        setStep(3);
    })
    .catch(e => showError(e.message))
    .finally(() => btn.disabled = false);
}

  function pushToDB() {
    var btn = document.getElementById('btnDB');
    btn.disabled = true; btn.textContent = 'Pushing to MySQL...';
    fetch('/api/load_db', { method: 'POST' })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.status !== 'ok') { showError(data.message); btn.disabled = false; btn.textContent = 'Push to MySQL'; return; }
        document.getElementById('insertedMsg').textContent = data.inserted + ' records inserted into BoomTown.expenses';
        document.getElementById('step4').classList.remove('hidden');
        setStep(4);
      })
      .catch(function(e) { showError('DB push failed: ' + e.message); btn.disabled = false; btn.textContent = 'Push to MySQL'; });
  }
</script>
</body>
</html>"""


@app.route("/")
def index():
    return HTML_PAGE, 200, {"Content-Type": "text/html"}


@app.route("/api/validate", methods=["POST"])
def validate_upload():
    results = {}

    def clean_catering(df):
        df = df.copy()
        df["Total_Spend"] = df["Headcount"] * df["Price_Per_Head"]
        df.to_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_catering.csv"), index=False)
        return df

    def clean_camera(df):
        df = df.copy()
        df["Daily_Rate"] = pd.to_numeric(df["Daily_Rate"].astype(str).str.replace("AED", "").str.strip(), errors="coerce")
        df["Days"] = pd.to_numeric(df["Days"], errors="coerce")
        df["Total_Cost"] = df["Days"] * df["Daily_Rate"]
        df.to_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_camera_dept.csv"), index=False)
        return df

    def clean_transport(df):
        df = df.copy()
        for col in ["Driver_OT_Hours", "Fuel_AED", "Salik_Tolls"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Total_Transport_Cost"] = df["Fuel_AED"] + df["Salik_Tolls"] + df["Driver_OT_Hours"] * 50
        df.to_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_Transport_Dubai.csv"), index=False)
        return df

    def clean_talent(df):
        df = df.copy()
        df["Contract_Fee"] = pd.to_numeric(df["Contract_Fee"], errors="coerce")
        df = df[df["Status"].str.lower() != "pending"]
        df.to_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_Talent_Payout.csv"), index=False)
        return df

    cleaners = {
        "catering": clean_catering,
        "camera": clean_camera,
        "transport": clean_transport,
        "talent": clean_talent,
    }

    for dept in ["catering", "camera", "transport", "talent"]:
        f = request.files.get(dept)
        if f is None:
            results[dept] = {"status": "missing", "message": "File not uploaded"}
            continue
        try:
            df = pd.read_csv(io.StringIO(f.read().decode("utf-8")))
            missing = REQUIRED_COLS[dept] - set(df.columns)
            if missing:
                results[dept] = {"status": "error", "message": "Missing columns: " + ", ".join(missing), "rows": len(df)}
            else:
                cleaned = cleaners[dept](df)
                results[dept] = {"status": "ok", "message": "Validated & cleaned", "rows": len(cleaned)}
        except Exception as e:
            results[dept] = {"status": "error", "message": str(e)}

    all_ok = all(v.get("status") == "ok" for v in results.values())
    return jsonify({"results": results, "ready_to_combine": all_ok})


@app.route("/api/combine", methods=["POST"])
def combine():
    try:
        cam = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_camera_dept.csv"))[["Date", "Total_Cost"]].rename(columns={"Date": "date", "Total_Cost": "amount"})
        cam["department"] = "camera"
        cam["project_id"] = 1

        cat = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_catering.csv"))[["Date", "Total_Spend"]].rename(columns={"Date": "date", "Total_Spend": "amount"})
        cat["department"] = "catering"
        cat["project_id"] = 1

        trn = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_Transport_Dubai.csv"))[["Date", "Total_Transport_Cost"]].rename(columns={"Date": "date", "Total_Transport_Cost": "amount"})
        trn["department"] = "transport"
        trn["project_id"] = 1

        tal = pd.read_csv(os.path.join(UPLOAD_FOLDER, "Cleaned_Talent_Payout.csv"))[["Contract_Fee"]].rename(columns={"Contract_Fee": "amount"})
        tal["department"] = "talent"
        tal["date"] = "2026-04-01"
        tal["project_id"] = 1

        combined = pd.concat([cam, cat, trn, tal], ignore_index=True)[["project_id", "department", "amount", "date"]]
        combined.to_csv(os.path.join(COMBINED_FOLDER, "combined_expenses.csv"), index=False)
        total_sum = float(combined["amount"].sum())
        avg_spend = float(combined["amount"].mean())
        summary_df = combined.groupby("department")["amount"].agg(total="sum", count="count").reset_index()
        
        # Find the "Top Spender"
        top_row = summary_df.loc[summary_df['total'].idxmax()]
        concentration = (top_row['total'] / total_sum) * 100

        return jsonify({
            "status": "ok",
            "rows": len(combined),
            "total_aed": round(total_sum, 2),
            "average_spend": round(avg_spend, 2),
            "top_dept": top_row['department'],
            "concentration": round(concentration, 1),
            "summary": summary_df.to_dict(orient="records")
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/load_db", methods=["POST"])
def load_db():
    try:
        df = pd.read_csv(os.path.join(COMBINED_FOLDER, "combined_expenses.csv"))
        con = pymysql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT,
                department VARCHAR(50),
                amount DECIMAL(12,2),
                expense_date DATE
            )
        """)
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO expenses (project_id, department, amount, expense_date) VALUES (%s, %s, %s, %s)",
                (int(row["project_id"]), row["department"], float(row["amount"]), row["date"])
            )
        con.commit()
        cursor.close()
        con.close()
        return jsonify({"status": "ok", "inserted": len(df)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    try:
        con = pymysql.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM expenses ORDER BY expense_date", con)
        con.close()
        return jsonify({"status": "ok", "data": df.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
