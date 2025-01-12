# BHA (Bottom Hole Assembly) Designer

![BHA Designer Logo](docs/images/bha_logo.png)

A web application for designing and managing Bottom Hole Assembly (BHA) configurations in drilling operations.

## Features

- **Component Management**
  - Create and manage BHA components
  - Upload component images
  - Track component specifications (length, diameter, weight)
  - ![Component List](docs/images/component_list.png)

- **BHA Configuration**
  - Design complete BHA configurations
  - Drag-and-drop component arrangement
  - Automatic length calculation
  - Visual representation of the assembly
  - ![BHA Configuration](docs/images/bha_config.png)

- **Visual Representation**
  - Automatic generation of BHA diagrams
  - Component-wise length labeling
  - Professional technical drawing style
  - ![BHA Diagram](docs/images/bha_diagram.png)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bha-designer.git
cd bha-designer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Technologies Used

- Django 4.x
- Python 3.x
- Bootstrap 5
- PIL (Python Imaging Library)
- SQLite/PostgreSQL

## Project Structure

```
bha_designer/
├── bha_app/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── media/
│   ├── bha_components/
│   └── bha_configurations/
├── static/
├── manage.py
└── requirements.txt
```

## Usage

1. **Adding Components**
   - Navigate to Components section
   - Click "Add New Component"
   - Fill in component details and upload image
   - Save component

2. **Creating BHA Configuration**
   - Go to "Create BHA" section
   - Name your configuration
   - Add components in desired order
   - Set quantities for each component
   - Save configuration

3. **Viewing Configurations**
   - Access saved configurations from dashboard
   - View detailed technical drawings
   - Check component specifications
   - Export or share designs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors
- Inspired by real-world drilling operations
- Built with Django and modern web technologies

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/bha-designer](https://github.com/yourusername/bha-designer)
```

To complete this README, you'll need to:

1. Create a `docs/images` directory in your project
2. Add relevant screenshots:
   - Logo image
   - Component list screenshot
   - BHA configuration interface screenshot
   - Generated BHA diagram example

3. Update the following placeholders:
   - Your GitHub username
   - Your contact information
   - Actual project repository URL
   - Social media links

4. Create a LICENSE file if you haven't already

The README provides a comprehensive overview of your project, making it easy for others to understand, install, and use your BHA Designer application.
