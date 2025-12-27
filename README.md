# PARTS — Package And Reference Tagging System

**PARTS** is a configurable labelling engine for electronic components.  
It generates clean, consistent PDF labels using accurate symbols, package drawings and specifications for resistors, diodes, capacitors, active devices and more.

Originally based on **Finomnis/ResistorLabels**, the project has grown into a general-purpose labelling system suitable for any electronics lab, workshop or makerspace.

## Features

- PDF label generation using ReportLab  
- Automatic electrical symbol rendering  
- Automatic package drawing (axial resistors, LEDs, diodes, transistors, etc.)  
- JSON-driven configuration  
- Support for standard label sheets (Avery 5260, Avery L7157, etc.)  
- Modular architecture (components, symbols, packages, layouts, models)

## Example Output

*(Insert example images or PDF previews here)*


## Installation

### Requirements
- Python 3.10+
- `reportlab` library

### Install dependencies

```bash
pip install reportlab
```

### Clone PARTS

```bash
git clone <repo-url>
cd PARTS
```

## Usage

### Generate a sheet

```bash
python main.py ./src/config/resistors_e12_config.json
```

### Change label template

Inside your config JSON:

```json
{
  "layout": "AVERY_L7157"
}
```

### Add your own components

Edit or create a configuration file:

```json
{
  "title": "My Components",
  "layout": "AVERY_5260",
  "labels": [
    { "kind": "resistor", "value_ohms": 4700 },
    { "kind": "diode", "part_number": "1N4148", "subtype": "diode" },
    { "kind": "capacitor", "value": "10nF", "voltage": "50V" }
  ]
}
```

<!-- ## Extending PARTS

To add a new component type:

1. Add a dataclass to `src/model/devices.py`
2. Create `src/components/<name>_renderer.py`
3. Add symbols (optional) in `src/symbols/`
4. Add physical package rendering (optional) in `src/packages/`
5. Register the renderer in `render_engine.py`

ARC is designed to scale to:
- Transistor / MOSFET symbol sets
- IC outline renderers
- Multi-component kit sheets
- QR-code-linked datasheets
- Custom artwork or company branding -->

## Credits

PARTS began as a fork of:

**Finomnis – ResistorLabels**  
https://github.com/Finomnis/ResistorLabels

It has since been expanded into a fully general electrical component labelling tool.

## License

*(Insert your chosen license here)*

