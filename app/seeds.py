"""Comandos CLI: `flask init-db` crea las tablas, `flask seed` carga datos
de ejemplo (usuarios, temas, banco de preguntas e insignias).

Las preguntas son contenido de muestra para el MVP; la empresa las
reemplaza/amplía desde el panel de administración (Función 3).
"""
import click
from flask.cli import with_appcontext

from .extensions import db
from .models import Badge, Choice, Question, Topic, User
from .services.gamification_service import BADGE_CATALOG

USERS = [
    {"email": "admin@seguridaddeoro.co", "full_name": "Administrador Plataforma",
     "role": "admin", "password": "Admin123*"},
    {"email": "supervisor@seguridaddeoro.co", "full_name": "Carlos Méndez",
     "role": "supervisor", "password": "Super123*"},
    {"email": "guarda1@seguridaddeoro.co", "full_name": "Andrés Rojas",
     "role": "guarda", "password": "Guarda123*"},
    {"email": "guarda2@seguridaddeoro.co", "full_name": "Luisa Pardo",
     "role": "guarda", "password": "Guarda123*"},
    {"email": "guarda3@seguridaddeoro.co", "full_name": "Jorge Quintero",
     "role": "guarda", "password": "Guarda123*"},
]

TOPICS = [
    {"name": "Control de Accesos", "level": 1,
     "description": "Protocolos de verificación, manejo de bitácoras y sistemas electrónicos de ingreso."},
    {"name": "Rondas de Vigilancia", "level": 2,
     "description": "Patrullaje preventivo e identificación de vulnerabilidades físicas."},
    {"name": "Comunicación Efectiva", "level": 1,
     "description": "Radiocomunicación, códigos 10 y reportes claros."},
    {"name": "Gestión de Crisis", "level": 4,
     "description": "Evacuación, primeros auxilios básicos y contención de incidentes."},
    {"name": "Leyes y Normatividad", "level": 1,
     "description": "Marco legal de la vigilancia privada en Colombia y Habeas Data."},
]

# (tema, dificultad, pregunta, [opciones], índice_correcta, explicación)
QUESTIONS = [
    ("Control de Accesos", "facil",
     "¿Qué debe hacer el guarda antes de autorizar el ingreso de un visitante?",
     ["Verificar su identidad y registrar el ingreso en la bitácora",
      "Dejarlo pasar si dice que tiene una cita",
      "Pedirle que espere sin registrar nada",
      "Llamar a la policía"],
     0, "Todo ingreso debe verificarse y quedar registrado en la bitácora o sistema de control."),
    ("Control de Accesos", "facil",
     "Un proveedor llega con un paquete y no está en la lista de autorizados. ¿Qué procede?",
     ["Recibir el paquete sin preguntar",
      "Confirmar la autorización con el responsable interno antes de permitir el ingreso",
      "Negar el ingreso definitivamente",
      "Dejar el paquete en la portería sin registro"],
     1, "Ante una visita no anunciada se confirma con el responsable interno y se registra la decisión."),
    ("Control de Accesos", "media",
     "¿Cuál es el propósito principal de la requisa de salida de vehículos?",
     ["Demorar la salida para controlar el tráfico",
      "Revisar el estado mecánico del vehículo",
      "Prevenir la extracción no autorizada de bienes de la instalación",
      "Verificar el SOAT del conductor"],
     2, "La requisa de salida busca evitar pérdida de activos, siempre con respeto y protocolo."),
    ("Control de Accesos", "media",
     "El sistema biométrico falla durante el turno. ¿Cuál es la acción correcta?",
     ["Suspender todos los ingresos hasta que lo reparen",
      "Aplicar el procedimiento manual de verificación y reportar la falla",
      "Permitir el ingreso libre mientras tanto",
      "Anotar los nombres de memoria y registrarlos después"],
     1, "Siempre existe un procedimiento alterno manual; la falla se reporta de inmediato."),
    ("Control de Accesos", "dificil",
     "Una persona presenta una orden judicial para ingresar. El protocolo indica:",
     ["Impedir el ingreso porque no está en la lista",
      "Permitir el ingreso inmediato sin verificación",
      "Verificar el documento, informar al jefe inmediato y registrar el procedimiento",
      "Pedirle que regrese al día siguiente"],
     2, "Las órdenes de autoridad se atienden verificando autenticidad e informando a la cadena de mando."),

    ("Rondas de Vigilancia", "facil",
     "¿Por qué las rondas deben hacerse en horarios y rutas variables?",
     ["Para terminar más rápido el turno",
      "Para evitar que terceros predigan el patrón de vigilancia",
      "Porque lo exige el reglamento de tránsito",
      "Para ahorrar batería del radio"],
     1, "Un patrón predecible facilita que un intruso planifique; la variación es una medida preventiva."),
    ("Rondas de Vigilancia", "facil",
     "Durante la ronda encuentras una puerta de emergencia abierta que debería estar cerrada. ¿Qué haces primero?",
     ["Cerrarla y seguir la ronda sin avisar",
      "Reportar el hallazgo por radio antes de intervenir el área",
      "Entrar a investigar solo y en silencio",
      "Esperar al siguiente turno para informar"],
     1, "Primero se reporta: puede tratarse de un ingreso en curso y el guarda no debe exponerse solo."),
    ("Rondas de Vigilancia", "media",
     "¿Qué es un punto de marcación (checkpoint) en una ronda?",
     ["Un lugar de descanso del guarda",
      "Un punto de control donde se registra el paso del vigilante",
      "La caseta principal de la portería",
      "El punto de encuentro en caso de evacuación"],
     1, "Los puntos de marcación dejan evidencia verificable de que la ronda se realizó completa."),
    ("Rondas de Vigilancia", "media",
     "Identificas una cerca perimetral con un corte pequeño. No hay señales de intrusión. ¿Qué procede?",
     ["Repararla tú mismo al final del turno",
      "Ignorarla por ser un daño menor",
      "Reportarla como vulnerabilidad, documentarla y aumentar la frecuencia de ronda en el sector",
      "Cubrirla con cinta y continuar"],
     2, "Toda vulnerabilidad física se documenta y reporta; puede ser preparación de un ingreso futuro."),
    ("Rondas de Vigilancia", "dificil",
     "En una ronda nocturna observas a dos personas merodeando fuera del perímetro. La acción correcta es:",
     ["Salir a confrontarlas de inmediato",
      "Observar, registrar descripción y reportar a la central sin abandonar el puesto",
      "Apagar las luces para que no te vean",
      "Disparar al aire como advertencia"],
     1, "El guarda observa y reporta; la confrontación fuera del perímetro excede sus funciones y lo expone."),

    ("Comunicación Efectiva", "facil",
     "En radiocomunicación, ¿qué significa el código 10-4?",
     ["Solicito apoyo urgente",
      "Mensaje recibido / entendido",
      "Cambio de turno",
      "Falsa alarma"],
     1, "10-4 confirma la recepción del mensaje. Es el código más usado en la operación."),
    ("Comunicacion Efectiva", "facil",
     "¿Cuál es la forma correcta de iniciar una transmisión de radio?",
     ["Hablar de inmediato sin identificarse",
      "Identificarse e identificar al destinatario antes del mensaje",
      "Silbar para llamar la atención",
      "Esperar a que alguien más hable primero"],
     1, "La identificación de origen y destino evita confusiones en canal compartido."),
    ("Comunicación Efectiva", "media",
     "Un reporte de novedad debe contener como mínimo:",
     ["Solo la hora del incidente",
      "Qué pasó, dónde, cuándo, quiénes están involucrados y qué acción se tomó",
      "La opinión personal del guarda sobre el culpable",
      "Únicamente el nombre del supervisor de turno"],
     1, "El reporte completo (qué, dónde, cuándo, quién, acción) permite decisiones rápidas y trazabilidad."),
    ("Comunicación Efectiva", "media",
     "Durante una emergencia el canal de radio está saturado. ¿Qué debes hacer?",
     ["Gritar más fuerte que los demás",
      "Usar la palabra de prioridad establecida y transmitir solo lo esencial",
      "Cambiar de canal sin avisar",
      "Apagar el radio hasta que se calme la situación"],
     1, "Los protocolos de prioridad existen para que la información crítica pase primero."),
    ("Comunicación Efectiva", "dificil",
     "Recibes una instrucción por radio que contradice el procedimiento escrito del puesto. ¿Cómo actúas?",
     ["La ignoras por completo",
      "La cumples sin cuestionar",
      "Confirmas la instrucción, dejas constancia de quién la emitió y escalas la discrepancia",
      "Abandonas el puesto para verificar en persona"],
     2, "Ante contradicción se confirma, se deja evidencia y se escala: protege al guarda y a la operación."),

    ("Gestión de Crisis", "facil",
     "¿Cuál es la prioridad número uno en cualquier emergencia?",
     ["Proteger los bienes de la empresa",
      "La vida e integridad de las personas",
      "Encontrar al responsable",
      "Evitar daños a la imagen de la compañía"],
     1, "La vida humana siempre está por encima de bienes, procesos e imagen."),
    ("Gestión de Crisis", "media",
     "En una evacuación, el rol del guarda de seguridad es:",
     ["Salir primero para mostrar la ruta",
      "Orientar a las personas hacia las rutas y puntos de encuentro establecidos",
      "Bloquear las salidas para controlar el flujo",
      "Quedarse a proteger los equipos"],
     1, "El guarda orienta y apoya la evacuación según el plan de emergencias del puesto."),
    ("Gestión de Crisis", "media",
     "Encuentras a una persona inconsciente que respira. Mientras llega la ayuda médica, debes:",
     ["Darle agua para reanimarla",
      "Moverla a una silla",
      "Colocarla en posición lateral de seguridad y monitorear su respiración",
      "Aplicar compresiones torácicas de inmediato"],
     2, "Si respira, la posición lateral de seguridad protege la vía aérea; las compresiones son solo para paro."),
    ("Gestión de Crisis", "dificil",
     "Se reporta un artefacto sospechoso en la recepción. La acción correcta es:",
     ["Examinarlo y moverlo a un lugar despejado",
      "No tocarlo, aislar el área, evacuar y notificar a las autoridades",
      "Cubrirlo con un objeto pesado",
      "Tomarle fotos de cerca para el reporte"],
     1, "Nunca se manipula un artefacto sospechoso: aislar, evacuar y dejar actuar a los expertos."),
    ("Gestión de Crisis", "dificil",
     "Durante un hurto en curso con personas armadas, el protocolo para el guarda desarmado es:",
     ["Intervenir físicamente para detener el hurto",
      "Priorizar la seguridad de las personas, observar detalles y alertar a las autoridades sin confrontar",
      "Perseguir a los responsables al salir",
      "Negociar directamente con los asaltantes"],
     1, "Sin medios de defensa, confrontar multiplica el riesgo; observar y alertar salva vidas y aporta a la investigación."),

    ("Leyes y Normatividad", "facil",
     "¿Qué entidad ejerce control y vigilancia sobre los servicios de vigilancia y seguridad privada en Colombia?",
     ["La Policía de Tránsito",
      "La Superintendencia de Vigilancia y Seguridad Privada",
      "El Ministerio de Cultura",
      "La DIAN"],
     1, "La SuperVigilancia regula, autoriza y sanciona a las empresas y al personal del sector."),
    ("Leyes y Normatividad", "media",
     "La Ley 1581 de 2012 (Habeas Data) obliga al guarda que maneja registros de visitantes a:",
     ["Compartir los datos con quien los solicite",
      "Tratar los datos personales solo para la finalidad autorizada y protegerlos de acceso indebido",
      "Publicar la lista de visitantes diariamente",
      "Conservar los datos en su teléfono personal"],
     1, "Los datos de visitantes son datos personales: finalidad específica, confidencialidad y custodia."),
    ("Leyes y Normatividad", "media",
     "¿Qué es la legítima defensa según el marco legal colombiano?",
     ["Cualquier uso de la fuerza por parte del guarda",
      "La respuesta proporcional y necesaria ante una agresión injusta, actual o inminente",
      "El derecho a retener personas sospechosas por 24 horas",
      "El uso del arma en cualquier situación de riesgo"],
     1, "La defensa debe ser necesaria y proporcional a la agresión; el exceso genera responsabilidad penal."),
    ("Leyes y Normatividad", "dificil",
     "Un guarda retiene a una persona sorprendida en flagrancia. Legalmente debe:",
     ["Mantenerla retenida hasta el final del turno",
      "Interrogarla para obtener una confesión",
      "Ponerla a disposición de la autoridad de manera inmediata",
      "Imponerle una sanción económica"],
     2, "La aprehensión en flagrancia obliga a entrega inmediata a la autoridad; retener más tiempo es ilegal."),
    ("Leyes y Normatividad", "dificil",
     "El guarda conoce información confidencial del cliente por su trabajo. Divulgarla constituye:",
     ["Una falta menor sin consecuencias",
      "Un derecho de libre expresión",
      "Una violación del deber de reserva con consecuencias laborales y legales",
      "Algo permitido si ya no trabaja allí"],
     2, "El deber de confidencialidad subsiste incluso después de terminar el contrato."),
]


def run_seed() -> dict:
    """Inserta datos solo si la base está vacía. Devuelve el conteo creado."""
    created = {"users": 0, "topics": 0, "questions": 0, "badges": 0}

    if User.query.count() == 0:
        for data in USERS:
            user = User(email=data["email"], full_name=data["full_name"],
                        role=data["role"])
            user.set_password(data["password"])
            db.session.add(user)
            created["users"] += 1

    if Topic.query.count() == 0:
        topics = {}
        for data in TOPICS:
            topic = Topic(**data)
            db.session.add(topic)
            topics[data["name"]] = topic
        created["topics"] = len(topics)
        db.session.flush()

        for topic_name, difficulty, text, options, correct_idx, explanation in QUESTIONS:
            # tolerar pequeñas variaciones de tildes en la tabla de arriba
            topic = topics.get(topic_name) or next(
                t for n, t in topics.items()
                if n.lower().replace("ó", "o") == topic_name.lower().replace("ó", "o"))
            question = Question(topic_id=topic.id, text=text,
                                difficulty=difficulty, explanation=explanation)
            for i, option in enumerate(options):
                question.choices.append(Choice(text=option, is_correct=i == correct_idx))
            db.session.add(question)
            created["questions"] += 1

    if Badge.query.count() == 0:
        for data in BADGE_CATALOG:
            db.session.add(Badge(**data))
            created["badges"] += 1

    db.session.commit()
    return created


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Crea todas las tablas."""
    db.create_all()
    click.echo("Tablas creadas.")


@click.command("seed")
@with_appcontext
def seed_command():
    """Carga datos de ejemplo (idempotente: solo si la base está vacía)."""
    created = run_seed()
    click.echo(f"Seed completado: {created}")
