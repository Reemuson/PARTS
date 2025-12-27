# PARTS — Package And Reference Tagging System

**PARTS** is a Python-based labelling engine for electronic components.
It generates clean, consistent PDF labels with accurate electrical symbols,
simplified-style package drawings and key specifications, suitable for electronics
labs, workshops and makerspaces.

PARTS is designed for engineers who care about correctness, repeatability and
long-term component organisation.

Originally based on **Finomnis/ResistorLabels**, PARTS has evolved into a
general-purpose component labelling system covering discrete passives, diodes,
transistors and power devices.

---

## Why PARTS?

Most label tools only print text.

PARTS prints meaning:

- Electrical symbols that match the device type
- Physical package drawings that match the real component
- Key electrical limits at a glance
- Consistent formatting across your entire lab

If you have ever pulled a part from a drawer and wondered “what exactly is this?”,
PARTS is for you.

---

## Features

- PDF label generation using ReportLab
- Automatic electrical symbol rendering
- Accurate package drawings
- JSON-driven configuration
- Mixed component sheets
- Support for common label templates:
  - Avery 5260
  - Avery L7157
  - Avery L7144
- Modular architecture:
  - components
  - symbols
  - packages
  - layouts
  - render engine

---

## Documentation

Full documentation is available in the **[GitHub Wiki](https://github.com/Reemson/PARTS/wiki)**:

- Getting Started
- Installation
- Command-Line Interface
- Configuration Reference
- Supported Components
- Supported Packages
- Roadmap

---

## Example Output

<p align="center">
  <img src="docs/images/led_labels.jpg" width="30%">
  <img src="docs/images/transistor_labels.jpg" width="30%">
  <img src="docs/images/example_output.jpg" width="30%">
</p>

---

## Example Configuration

A minimal example:

```json
{
  "layout": "AVERY_5260",
  "labels": [
    { "kind": "resistor", "value_ohms": 4700 }
  ]
}
```

---

## Supported Components

PARTS supports a wide range of discrete components including resistors,
diodes, transistors and power devices.

See the **[wiki](https://github.com/Reemson/PARTS/wiki/Supported-Components)** for the authoritative list of supported components, subtypes and JSON schema.

---

## Contributing and Extending

PARTS is designed to be modular and contributor-friendly.

Guidelines for adding new components, symbols and packages are documented
in the **[wiki](https://github.com/Reemson/PARTS/wiki/Contributing)**.

---

## Credits

PARTS began as a fork of:

ResistorLabels by Finomnis  
https://github.com/Finomnis/ResistorLabels

Copyright (c) 2020 Martin Stumpf  
Licensed under the MIT License.

This project substantially extends the original work.

---

## License

MIT License. See `LICENSE`.
