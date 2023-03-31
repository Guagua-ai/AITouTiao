def format_results(relevant_results):
    html_template = """
    <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Content</th>
                        <th>Translated Content</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
    </html>
    """

    table_rows = ""
    for result in relevant_results:
        table_rows += f"""
        <tr>
            <td>{result[1]}</td>
            <td>{result[2]}</td>
            <td>{result[3]}</td>
        </tr>
        """

    return html_template.format(table_rows=table_rows)
