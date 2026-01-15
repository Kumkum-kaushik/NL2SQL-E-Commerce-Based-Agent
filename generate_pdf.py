import markdown2
from xhtml2pdf import pisa
import os

def convert_md_to_pdf(source_md, output_pdf):
    # 1. Read Markdown
    with open(source_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 2. Convert to HTML
    html_content = markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks", "cuddled-lists"])

    # 3. Add styling
    styled_html = f"""
    <html>
    <head>
    <style>
        @page {{
            size: letter;
            margin: 2cm;
            @frame footer_frame {{           /* Static Footer Frame */
                -pdf-frame-content: footer_content;
                bottom: 1cm;
                margin-left: 1cm;
                margin-right: 1cm;
                height: 1cm;
            }}
        }}

        body {{
            font-family: Helvetica, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333333;
        }}

        h1 {{
            font-size: 24pt;
            color: #1a73e8;
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}

        h2 {{
            font-size: 18pt;
            color: #1a73e8;
            margin-top: 20px;
            margin-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: bold;
            color: #555555;
            margin-top: 15px;
            margin-bottom: 5px;
        }}

        p {{
            margin-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            margin-bottom: 15px;
        }}

        th {{
            background-color: #f2f2f2;
            color: #333;
            font-weight: bold;
            padding: 8px;
            border: 1px solid #ddd;
            text-align: left;
        }}

        td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}

        code {{
            font-family: Courier, monospace;
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 90%;
        }}

        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow-x: auto;
            font-family: Courier, monospace;
            font-size: 9pt;
        }}

        ul, ol {{
            margin-bottom: 10px;
            padding-left: 20px;
        }}
        
        li {{
            margin-bottom: 5px;
        }}
    </style>
    </head>
    <body>
    {html_content}
    <div id="footer_content" style="text-align: center; color: #666; font-size: 9pt;">
        Page <pdf:pagenumber> of <pdf:pagecount>
    </div>
    </body>
    </html>
    """

    # 4. Generate PDF
    print(f"Generating PDF: {output_pdf}...")
    with open(output_pdf, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)

    if pisa_status.err:
        print("Error generating PDF")
    else:
        print("Success!")

if __name__ == "__main__":
    convert_md_to_pdf("FINAL_PROJECT_REPORT.md", "NL2SQL_Project_Report.pdf")
