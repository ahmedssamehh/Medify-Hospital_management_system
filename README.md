\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}

\title{\textbf{Medify - A Comprehensive Hospital Management System}}
\author{}
\date{}

\begin{document}

\maketitle

\section*{Introduction}
\textbf{Medify} is a hospital management system designed to optimize hospital operations. It integrates patient history, doctor and pharmacy management, and appointment scheduling into a single platform.

\section*{Features}
\begin{itemize}
    \item Patient registration.
    \item Assigning doctors.
    \item Managing prescriptions.
    \item Tracking pharmacies.
    \item Online appointment booking and doctor profiles.
\end{itemize}

\section*{Technologies Used}
\begin{itemize}
    \item \textbf{Backend}: Flask (Python).
    \item \textbf{Frontend}: HTML, CSS, JavaScript, and Bootstrap for a responsive user interface.
    \item \textbf{Database}: MySQL for structured data management.
    \item \textbf{APIs}: Swagger for documentation, Postman for testing.
    \item \textbf{Deployment}: Docker for containerized applications.
\end{itemize}

\section*{Installation and Running Steps}

Follow these steps to set up and run the project locally:

\begin{enumerate}
    \item \textbf{Clone the Repository}:
    \begin{verbatim}
    git clone https://github.com/username/Medify.git
    cd Medify
    \end{verbatim}

    \item \textbf{Install Backend Dependencies}:
    Ensure you have Python installed. Then, set up a virtual environment and install the required packages:
    \begin{verbatim}
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    \end{verbatim}

    \item \textbf{Set Up the Database}:
    \begin{itemize}
        \item Install MySQL.
        \item Create a database named \texttt{medify}.
        \item Configure your database credentials in the project’s settings.
    \end{itemize}

    \item \textbf{Run the Backend Server}:
    \begin{verbatim}
    flask run
    \end{verbatim}

    \item \textbf{Set Up Frontend}:
    No framework required for the frontend. Just open \texttt{index.html} in your browser.

    \item \textbf{Use Docker (Optional)}:
    If you want to deploy using Docker, ensure Docker is installed, and then build and run the container:
    \begin{verbatim}
    docker build -t medify .
    docker run -p 5000:5000 medify
    \end{verbatim}
\end{enumerate}

\section*{Usage}
\begin{itemize}
    \item \textbf{Register/Login} as a patient, doctor, or administrator.
    \item \textbf{Book Appointments} through the patient interface.
    \item \textbf{Manage Prescriptions} via the doctor interface.
    \item \textbf{Track Pharmacies} and stock levels.
\end{itemize}

\section*{Screenshots}
Include screenshots here for visual representation:
\begin{itemize}
    \item Patient Registration Page.
    \item Doctor Profile View.
    \item Appointment Booking Interface.
    \item Admin Dashboard.
\end{itemize}

\section*{Contributing}
The project is maintained by:
\begin{itemize}
    \item \href{https://github.com/motarek122112}{@motarek122112}
    \item \href{https://github.com/seifamr062}{@seifamr062}
    \item \href{https://github.com/shahdTarekk}{@shahdTarekk}
    \item \href{https://github.com/salmaZZiada}{@salmaZZiada}
\end{itemize}

\section*{License}
This project is licensed under the MIT License.

\end{document}
