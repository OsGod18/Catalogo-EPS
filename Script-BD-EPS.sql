CREATE DATABASE catalogo_eps;

USE catalogo_eps;

-- TABLA USUARIOS

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    pin VARCHAR(4) NOT NULL
);


-- TABLA CLIENTES

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    direccion VARCHAR(100) NOT NULL,
    saldo DECIMAL(10,2) NOT NULL DEFAULT 0,
    es_empleado BOOLEAN NOT NULL DEFAULT FALSE,
    pin VARCHAR(4) NOT NULL
);


-- TABLA EMPLEADOS

CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL UNIQUE,
    id_empleado VARCHAR(4) NOT NULL UNIQUE,
    contrasena VARCHAR(10) NOT NULL,
    cargo VARCHAR(50) DEFAULT 'Empleado Junior',
    salario DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE CASCADE
);

-- TABLA MEDICAMENTOS

CREATE TABLE medicamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_medicamento VARCHAR(100) NOT NULL,
    formula_quimica VARCHAR(200) NOT NULL,
    descripcion_medicamento TEXT NOT NULL,
    cantidad_pastas VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    incluido_pbs BOOLEAN NOT NULL,
    stock INT NOT NULL,
    imagen_card VARCHAR(200) NOT NULL,
    imagen_empaque VARCHAR(200) NOT NULL,
    imagen_producto VARCHAR(200) NOT NULL
);

-- TABLA SOLICITUDES

CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    tipo_persona ENUM('usuario', 'cliente') NOT NULL,
    medicamento_id INT NOT NULL,
    tipo_entrega VARCHAR(100) NOT NULL,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATE NOT NULL,
    FOREIGN KEY (medicamento_id)
    REFERENCES medicamentos(id)
);

-- TABLA TAREAS DE EMPLEADOS

CREATE TABLE tareas_empleado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    tipo_tarea VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    medicamento_id INT,
    objetivo INT NOT NULL,
    progreso INT DEFAULT 0,
    completada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (empleado_id)
        REFERENCES empleados(id),
    FOREIGN KEY (medicamento_id)
        REFERENCES medicamentos(id)
);

-- TABLA FECHAS DE ENVIO DE LOS MEDICAMENTOS

CREATE TABLE fechas_disponibles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE
);

INSERT INTO fechas_disponibles (fecha)
VALUES
('2026-05-20'),
('2026-05-23'),
('2026-05-26'),
('2026-05-29'),
('2026-06-02'),
('2026-06-05'),
('2026-06-08'),
('2026-06-12'),
('2026-06-15'),
('2026-06-18');


-- TABLA FACTURAS

CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    tipo_persona ENUM('usuario', 'cliente') NOT NULL,
    medicamento_id INT NOT NULL,
    solicitud_id INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_factura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_pago ENUM('eps', 'saldo_cliente') NOT NULL,
    FOREIGN KEY (medicamento_id)
    REFERENCES medicamentos(id),
    FOREIGN KEY (solicitud_id)
    REFERENCES solicitudes(id)
);


SELECT * FROM usuarios;

SELECT * FROM clientes;

SELECT * FROM empleados;

SELECT * FROM fechas_disponibles;


-- INSERT MEDICAMENTOS

INSERT INTO medicamentos (nombre_medicamento,formula_quimica,descripcion_medicamento,cantidad_pastas,precio,incluido_pbs,stock,imagen_card,imagen_empaque,imagen_producto)
VALUES

(
    'Amoxicilina',
    'C16H19N3O5S',
    'Antibiotico para infecciones bacterianas',
    '14',
    18000,
    TRUE,
    1030,
    'amox-primera-imagen.png',
    'amox-segunda-imagen.png',
    'amox-tercera-imagen.png'
),

(
    'Loratadina',
    'C22H23ClN2O2',
    'Antihistaminico para alergias',
    '20',
    12000,
    TRUE,
    332,
    'lora-primera-imagen.png',
    'lora-segunda-imagen.png',
    'lora-tercera-imagen.png'
),

(
    'Metformina',
    'C4H11N5',
    'Tratamiento para diabetes tipo 2',
    '30',
    25000,
    TRUE,
    129,
    'metfor-primera-imagen.png',
    'metfor-segunda-imagen.png',
    'metfor-tercera-imagen.png'
),

(
    'Omeprazol',
    'C17H19N3O3S',
    'Reductor de acido gastrico',
    '14',
    15000,
    TRUE,
    400,
    'ome-primera-imagen.png',
    'ome-segunda-imagen.png',
    'ome-tercera-imagen.png'
),

(
    'Salbutamol',
    'C13H21NO3',
    'Broncodilatador para el asma',
    '200 dosis',
    35000,
    TRUE,
    950,
    'salbu-primera-imagen.png',
    'salbu-segunda-imagen.png',
    'salbu-tercera-imagen.png'
),

(
    'Losartan',
    'C22H22ClN6O',
    'Tratamiento para hipertension',
    '30',
    22000,
    TRUE,
    1010,
    'losar-primera-imagen.png',
    'losar-segunda-imagen.png',
    'losar-tercera-imagen.png'
),

(
    'Atorvastatina',
    'C33H35FN2O5',
    'Medicamento para reducir colesterol',
    '30',
    28000,
    TRUE,
    680,
    'ator-primera-imagen.png',
    'ator-segunda-imagen.png',
    'ator-tercera-imagen.png'
),

(
    'Insulina',
    'C257H383N65O77S6',
    'Hormona para control de glucosa',
    '5 lapiceros',
    120000,
    TRUE,
    452,
    'insu-primera-imagen.png',
    'insu-segunda-imagen.png',
    'insu-tercera-imagen.png'
),

(
    'Diclofenaco',
    'C14H11Cl2NO2',
    'Analgésico y antiinflamatorio',
    '20',
    10000,
    TRUE,
    518,
    'diclo-primera-imagen.png',
    'diclo-segunda-imagen.png',
    'diclo-tercera-imagen.png'
),

(
    'Naproxeno',
    'C14H14O3',
    'Medicamento para dolor e inflamacion',
    '20',
    14000,
    TRUE,
    132,
    'napro-primera-imagen.png',
    'napro-segunda-imagen.png',
    'napro-tercera-imagen.png'
),

(
    'Enalapril',
    'C20H28N2O5',
    'Medicamento para presion arterial',
    '30',
    19000,
    TRUE,
    635,
    'ena-primera-imagen.png',
    'ena-segunda-imagen.png',
    'ena-tercera-imagen.png'
),

(
    'Cetirizina',
    'C21H25ClN2O3',
    'Tratamiento para alergias',
    '20',
    11000,
    TRUE,
    68,
    'ceti-primera-imagen.png',
    'ceti-segunda-imagen.png',
    'ceti-tercera-imagen.png'
);