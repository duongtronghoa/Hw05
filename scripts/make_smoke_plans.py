"""Create disposable one-user, one-iteration copies of the three HW05 plans."""

from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "smoke" / "plans"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for source in sorted((ROOT / "plans").glob("23120127_*.jmx")):
        tree = ET.parse(source)
        groups = tree.findall(".//ThreadGroup")
        if not groups:
            raise RuntimeError(f"No ThreadGroup in {source}")
        for i, group in enumerate(groups):
            group.set("enabled", "true" if i == 0 else "false")
            for name, value in (
                ("ThreadGroup.num_threads", "1"),
                ("ThreadGroup.ramp_time", "1"),
                ("ThreadGroup.scheduler", "false"),
                ("ThreadGroup.duration", ""),
            ):
                prop = group.find(f"./stringProp[@name='{name}']")
                if prop is not None:
                    prop.text = value
                else:
                    prop = group.find(f"./boolProp[@name='{name}']")
                    if prop is not None:
                        prop.text = value
            loops = group.find("./elementProp/collectionProp/elementProp/intProp[@name='LoopController.loops']")
            if loops is None:
                loops = group.find(".//intProp[@name='LoopController.loops']")
            if loops is None:
                raise RuntimeError(f"No loop count in {source}")
            loops.text = "1"
        for csv_path in tree.findall(".//CSVDataSet/stringProp[@name='filename']"):
            csv_path.text = str(ROOT / "data" / "admin${__threadNum}.csv")
        target = OUT / source.name
        tree.write(target, encoding="utf-8", xml_declaration=True)
        print(target)


if __name__ == "__main__":
    main()
