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

        summary = combined.groupby("department")["amount"].agg(total="sum", count="count").reset_index().to_dict(orient="records")
        return jsonify({"status": "ok", "rows": len(combined), "total_aed": round(float(combined["amount"].sum()), 2), "summary": summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500