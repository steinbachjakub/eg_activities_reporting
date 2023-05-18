import base64
from jinja2 import Environment, FileSystemLoader
from matplotlib import pyplot as plt
from pathlib import Path

with open("files/tempfig.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

environment = Environment(loader=FileSystemLoader("report_files"))
results_filename = "html_test.html"
results_template = environment.get_template("test_template.html")

context = {"chart_1_name": f"data:image/jpeg;base64,{encoded_string}"}

with open(results_filename, mode="w", encoding="utf-8") as results:
    results.write(results_template.render(context))
