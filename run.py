import argparse
import json
from dotenv import load_dotenv
from src.maintenance_ai.data_loader import load_data
from src.maintenance_ai.supervisor import SupervisorAgent

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run a synthetic turbine maintenance investigation.")
    parser.add_argument("--turbine", default="WT-03", help="Turbine ID, e.g. WT-03")
    parser.add_argument("--question", default=None, help="Optional investigation question")
    parser.add_argument("--llm", action="store_true", help="Use optional configured LLM synthesis")
    args = parser.parse_args()

    sensors, production, maintenance = load_data()
    supervisor = SupervisorAgent(sensors, production, maintenance, use_llm=args.llm)
    report = supervisor.investigate(args.turbine, args.question)
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    main()
