# CarbonDesk

CarbonDesk is our Compact Programming capstone project at FH Dortmund. We are
building a web platform for small and medium companies to track Scope 1, 2,
and 3 carbon emissions, view their results, and get AI suggestions for reducing
their footprint.

## Planned stack

| Technology | Purpose |
| --- | --- |
| Python | Main language for the backend and frontend. |
| Django | Backend logic, data validation, authentication, permissions, and database models through its ORM. |
| NiceGUI | Web interface with activity forms, CSV uploads, tables, dashboards, and an assistant chat. |
| PostgreSQL | Shared database for organisations, activity records, emission factors, targets, and chat history. |
| Plotly | Interactive emissions charts and trends. |
| OpenAI API | Explanations and reduction suggestions based on company emissions data. |
| Docker Compose | Run the application components and database together. |
| pytest | Automated tests for calculations and application behavior. |

Django handles the business rules and data access; NiceGUI provides the user
interface.

## Who does what

| Team member | Subsystem | Main responsibilities |
| --- | --- | --- |
| Guillermo Pérez Pérez | Emissions Data & Calculation | Activity entry and CSV import, input validation, emission factors, and conversion to kg CO2e. |
| Harib Khalid | Analytics Dashboard & Reporting | Charts, KPIs, filters, target progress, and PDF/CSV reports. |
| Omotunde Sholola Ganiyu | AI Sustainability Assistant | Company-data chat, reduction recommendations, savings estimates, and monthly summaries. |
| Omotunde Sholola Ganiyu | Users, Organisation & Targets | Login and roles, company structure, yearly reduction targets, alerts, and audit history. |

The team coordinates shared data models and interfaces so the subsystems work
together.

## Status

Initial project outline. Setup instructions, implemented UML diagrams, and the
team presentation video link will be added as development progresses.
