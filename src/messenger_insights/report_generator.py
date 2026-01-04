from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json
import plotly

class ReportGenerator:
    """Generates proper HTML reports from data metrics and Plotly figures."""
    
    def __init__(self, assets_dir: str = "assets"):
        self.env = Environment(loader=FileSystemLoader(assets_dir))
        self.template_name = "report_template.html"

    def generate_report(self, 
                        stats: dict, 
                        figures: dict, 
                        output_path: Path):
        """
        Renders the HTML report.
        stats: Dict containing simple metrics (total_messages, etc)
        figures: Dict of Plotly go.Figure objects {'timeline': fig, ...}
        """
        template = self.env.get_template(self.template_name)
        
        # Convert figures to JSON for embedding
        # We use plotly.io.to_json to get the JSON structure needed for Plotly.newPlot
        # Note: We need to parse it back to a python dict to pass to Jinja as a string, 
        # or just pass the string literals if we handle them carefully.
        # Actually simplest is to extract .data and .layout via to_json and let the template print it.
        
        context = stats.copy()
        
        for key, fig in figures.items():
            # Convert figure to JSON string
            json_str = json.dumps(json.loads(plotly.io.to_json(fig)))
            context[f"{key}_json"] = json_str
            
        html_content = template.render(**context)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == '__main__':
    # Verification
    print("ReportGenerator ready.")
