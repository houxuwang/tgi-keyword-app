from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
from io import BytesIO
from tgi_module import generate_tgi_dual_outputs

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def to_float_or_nan(val):
    try:
        return float(val)
    except:
        return np.nan

@app.route("/generate_tags", methods=["POST"])
def generate_tags():
    try:
        file = request.files["file"]
        df = pd.read_excel(file)
        
    
        params = request.form
        base_column = params.get("base_column")
   
    
        threshold = float(params.get("threshold", ""))
        tgi_threshold = float(params.get("tgi_threshold", ""))
        share_threshold = float(params.get("share_threshold", ""))
        seg_start_col = int(params["seg_start_col"])
        seg_end_col = int(params["seg_end_col"])
        tgi_start_col = int(params["tgi_start_col"])
        tgi_end_col = int(params["tgi_end_col"])

        result_df = generate_tgi_dual_outputs(
            df=df,
            base_column=base_column,
            threshold=threshold,
            tgi_threshold=tgi_threshold,
            share_threshold=share_threshold,
            seg_start_col=seg_start_col,
            seg_end_col=seg_end_col,
            tgi_start_col=tgi_start_col,
            tgi_end_col=tgi_end_col
        )

        # 输出为 Excel 文件流
        output = BytesIO()
        result_df.to_excel(output, index=True)
        output.seek(0)

        return send_file(output, download_name="标签输出.xlsx", as_attachment=True)

    except Exception as e:
        return f"<h3>出错了: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(debug=True)