import typer
from pathlib import Path
from messenger_insights.parsers import get_parser
from messenger_insights.processor import MessageProcessor
import json
from messenger_insights.analytics import MessageAnalytics
from messenger_insights.visualizations import MessageVisualizer
from messenger_insights.report_generator import ReportGenerator
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def analyze(
    data_dir: str = typer.Argument(..., help="Path to your unzipped data folder"),
    my_name: str = typer.Option(..., help="Your name as it appears in messages"),
    output_dir: str = typer.Option("output", help="Directory to save report"),
    static: bool = typer.Option(False, "--static", "-s", help="Export static HTML/PNG charts"),
    platform: str = typer.Option("facebook", help="Platform: facebook, instagram, or whatsapp")
) -> None:
    """Parses messages and generates a full analytics report."""
    console.print(f"[bold green]Scanning data in {data_dir} for {platform}...[/bold green]")
    
    try:
        # 1. Parse & Stream
        # Use factory to get correct parser
        parser = get_parser(platform, data_dir)
        
        # Generator function to inject title without loading everything to list
        def message_stream():
            for convo_data in parser.iter_conversations():
                title = convo_data.get('title', 'Unknown')
                for msg in convo_data.get('messages', []):
                    msg['conv_title'] = title
                    yield msg

        # 2. Process & Analyze in Single Pass
        # Manually iterate to feed both Processor (DF) and Analytics (Reactions)
        all_messages = []
        reaction_messages = [] 
        
        with console.status("[bold green]Streaming and parsing messages...[/bold green]"):
            for msg in message_stream():
                all_messages.append(msg)
                if 'reactions' in msg:
                    reaction_messages.append({
                        'sender_name': msg.get('sender_name'), 
                        'reactions': msg['reactions'],
                        'conv_title': msg.get('conv_title', 'Unknown')
                    })
        
        # Process the list (In-memory acceptable for <2GB JSONs)
        
        proc = MessageProcessor()
        df = proc.process_messages(all_messages, batch_size=50000)
        
        analytics = MessageAnalytics()
        reaction_map = analytics.analyze_reactions(reaction_messages)
        
        console.print(f"Processed [bold]{len(df)}[/bold] total messages.")
        
        if df.empty:
            console.print("[yellow]No messages found![/yellow]")
            return

        # 3. Analyze
        stats = analytics.calculate_response_times(df, my_name=my_name)
        init_rate = analytics.calculate_initiation_rate(df, my_name=my_name)
        emoji_data = analytics.extract_top_emojis(df, top_n=5)
        global_emoji_counts = emoji_data.get('global', {})
            
        # Print Summary Table
        table = Table(title="Messenger Insights V2")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Messages", str(len(df)))
        table.add_row("My Median Reply Time", f"{stats.get('my_median_reply_minutes', 'N/A')} min")
        table.add_row("Their Median Reply Time", f"{stats.get('their_median_reply_minutes', 'N/A')} min")
        table.add_row("My Initiation Rate", f"{init_rate.get('my_initiation_pct', 'N/A')}%")
        
        # Add Emoji Rows
        for sender, counts in global_emoji_counts.items():
            top_emoji = f"{counts[0][0]} ({counts[0][1]})" if counts else "None"
            table.add_row(f"{sender}'s Top Emoji", top_emoji)
        
        console.print(table)
        
        # 4. Visualize & Generate Report
        viz = MessageVisualizer()
        out_path = Path(output_dir)
        out_path.mkdir(exist_ok=True)
        
        # Prepare Data for Interactive Frontend
        # reaction_map contains 'global' and 'per_conv' 
        frontend_data = proc.prepare_frontend_data(df)
        emoji_raw = viz.get_emoji_data(global_emoji_counts)
        emoji_per_conv = {
            conv: viz.get_emoji_data(sender_counts) 
            for conv, sender_counts in emoji_data.get('per_conv', {}).items()
        }
        
        # Determine top emoji string
        top_emoji_display = "None"
        for sender, counts in global_emoji_counts.items():
             if counts:
                 top_emoji_display = counts[0][0]
                 break 
        
        # Convert top reactions to frontend format
        top_reactions_raw = viz.get_emoji_data(reaction_map.get('top_reactions', {}))
        top_reactions_per_conv = {
            conv: viz.get_emoji_data(sender_data)
            for conv, sender_data in reaction_map.get('top_reactions_per_conv', {}).items()
        }
        
        stats_dict = {
            "title": f"Report for {my_name}",
            "owner_name": my_name,
            "top_emoji": top_emoji_display,
            # Pass Raw JSONs as strings
            "frontend_data_json": json.dumps(frontend_data),
            "emoji_raw_json": json.dumps(emoji_raw),
            "emoji_per_conv_json": json.dumps(emoji_per_conv),
            "reaction_raw_json": json.dumps(reaction_map.get('global', {})),
            "reaction_per_conv_json": json.dumps(reaction_map.get('per_conv', {})),
            "top_reactions_json": json.dumps(top_reactions_raw),
            "top_reactions_per_conv_json": json.dumps(top_reactions_per_conv)
        }
        
        # Static Export Feature (Optional)
        figures = {} 
        if static:
            export_path = out_path / "charts"
            export_path.mkdir(exist_ok=True)
            console.print(f"[cyan]Exporting static charts to {export_path}...[/cyan]")
            
            # Generate Figures
            figures = {
                "timeline": viz.plot_timeline(df),
                "hourly": viz.plot_hourly_activity(df),
                "heatmap": viz.plot_activity_heatmap(df),
                "emoji": viz.plot_emoji_stats(emoji_counts),
                "pie": viz.plot_initiation_pie(init_rate)
            }
            
            for name, fig in figures.items():
                # HTML Export (Interactive Standalone)
                fig.write_html(export_path / f"{name}.html")
                
                # Image Export (Requires Kaleido)
                try:
                    # Provide width/height for consistent results
                    fig.write_image(export_path / f"{name}.png", width=1200, height=700, scale=2)
                except ImportError:
                    console.print(f"[yellow]Warning: Could not save {name}.png. Install 'kaleido' for image export.[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not save {name}.png: {e}[/yellow]")
        
        # Generate single HTML report
        reporter = ReportGenerator()
        report_file = out_path / "report.html"
        reporter.generate_report(stats_dict, figures, report_file)
        
        console.print(f"[bold green]✨ Data Processed! Report saved to: {report_file}[/bold green]")
        if static:
             console.print(f"[bold green]📊 Static charts saved to: {out_path}/charts/[/bold green]")
             
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Could not find message files in {data_dir}. Check the path and platform.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise  # Re-raise for debugging

if __name__ == "__main__":
    app()
