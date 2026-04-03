import sqlite3

def crear_conexion():
    return sqlite3.connect("recordatorios.db")

def crear_tabla():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recordatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        tarea TEXT,
        fecha TEXT,
        hora TEXT,
        frecuencia TEXT
    )
    """)

    conn.commit()
    conn.close()

def crear_tabla_mensajes():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        role TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()

def crear_tabla_seguimientos():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seguimientos_recordatorio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        recordatorio_id INTEGER,
        estado TEXT,
        fecha_envio TEXT
    )
    """)

    conn.commit()
    conn.close()

def guardar_recordatorio(data, usuario):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO recordatorios (usuario, tarea, fecha, hora, frecuencia)
    VALUES (?, ?, ?, ?, ?)
    """, (
        usuario,
        data.get("tarea"),
        data.get("fecha"),
        data.get("hora"),
        data.get("frecuencia")
    ))

    conn.commit()
    conn.close()

def obtener_recordatorios():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recordatorios")
    rows = cursor.fetchall()

    conn.close()
    return rows

def guardar_mensaje(usuario, role, content):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO mensajes (usuario, role, content)
    VALUES (?, ?, ?)
    """, (usuario, role, content))

    conn.commit()
    conn.close()


def obtener_mensajes_usuario(usuario, limite=10):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, content
    FROM mensajes
    WHERE usuario = ?
    ORDER BY id DESC
    LIMIT ?
    """, (usuario, limite))

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    return [{"role": role, "content": content} for role, content in rows]

def guardar_seguimiento(usuario, recordatorio_id, estado, fecha_envio):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO seguimientos_recordatorio (usuario, recordatorio_id, estado, fecha_envio)
    VALUES (?, ?, ?, ?)
    """, (usuario, recordatorio_id, estado, fecha_envio))

    conn.commit()
    conn.close()


def obtener_ultimo_seguimiento_pendiente(usuario):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, usuario, recordatorio_id, estado, fecha_envio
    FROM seguimientos_recordatorio
    WHERE usuario = ? AND estado = 'pendiente'
    ORDER BY id DESC
    LIMIT 1
    """, (usuario,))

    row = cursor.fetchone()
    conn.close()
    return row


def actualizar_estado_seguimiento(seguimiento_id, nuevo_estado):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE seguimientos_recordatorio
    SET estado = ?
    WHERE id = ?
    """, (nuevo_estado, seguimiento_id))

    conn.commit()
    conn.close()

def guardar_recordatorio_manual(usuario, tarea, fecha, hora, frecuencia):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO recordatorios (usuario, tarea, fecha, hora, frecuencia)
    VALUES (?, ?, ?, ?, ?)
    """, (usuario, tarea, fecha, hora, frecuencia))

    conn.commit()
    conn.close()


def obtener_recordatorio_por_id(recordatorio_id):
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, tarea, fecha, hora, frecuencia
    FROM recordatorios
    WHERE id = ?
    """, (recordatorio_id,))

    row = cursor.fetchone()
    conn.close()
    return row