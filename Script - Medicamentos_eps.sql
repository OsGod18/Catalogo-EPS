CREATE DATABASE catalogo_eps;
USE catalogo_eps;

DROP DATABASE catalogo_eps;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(20) UNIQUE,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion VARCHAR(200),
    pin VARCHAR(10)
);



CREATE TABLE medicamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_medicamento VARCHAR(100),
    formula_quimica VARCHAR(200),
    descripcion_medicamento TEXT,
    cantidad_pastas VARCHAR(50),
    stock INT,
    imagen_card VARCHAR(200),
    imagen_empaque VARCHAR(200),
    imagen_producto VARCHAR(200)
);

CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    medicamento_id INT,
    tipo_entrega VARCHAR(50),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATE,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);

INSERT INTO medicamentos 
(nombre_medicamento, formula_quimica, descripcion_medicamento, cantidad_pastas, stock, imagen_card, imagen_empaque, imagen_producto)
VALUES

('Amoxicilina','C16H19N3O5S','Antibiótico para infecciones bacterianas','14',1030,
'amox-primera-imagen.png',
'amox-segunda-imagen.png',
'amox-tercera-imagen.png'),

('Loratadina','C22H23ClN2O2','Antihistamínico para alergias','20',332,
'lora-primera-imagen.png',
'lora-segunda-imagen.png',
'lora-tercera-imagen.png'),

('Metformina','C4H11N5','Tratamiento para la diabetes tipo 2','30',129,
'metfor-primera-imagen.png',
'metfor-segunda-imagen.png',
'metfor-tercera-imagen.png'),

('Omeprazol','C17H19N3O3S','Reductor de ácido gástrico','14',400,
'ome-primera-imagen.png',
'ome-segunda-imagen.png',
'ome-tercera-imagen.png'),

('Salbutamol','C13H21NO3','Broncodilatador para el asma','200 dosis',950,
'salbu-primera-imagen.png',
'salbu-segunda-imagen.png',
'salbu-tercera-imagen.png'),

('Losartán','C22H22ClN6O','Tratamiento para la hipertensión','30',1010,
'losar-primera-imagen.png',
'losar-segunda-imagen.png',
'losar-tercera-imagen.png'),

('Atorvastatina','C33H35FN2O5','Para reducir el colesterol','30',680,
'ator-primera-imagen.png',
'ator-segunda-imagen.png',
'ator-tercera-imagen.png'),

('Insulina','C257H383N65O77S6','Hormona para el control de glucosa','5 lapiceros',452,
'insu-primera-imagen.png',
'insu-segunda-imagen.png',
'insu-tercera-imagen.png'),

('Diclofenaco','C14H11Cl2NO2','Analgésico potente','20',518,
'diclo-primera-imagen.png',
'diclo-segunda-imagen.png',
'diclo-tercera-imagen.png'),

('Naproxeno','C14H14O3','Dolor e inflamación','20',132,
'napro-primera-imagen.png',
'napro-segunda-imagen.png',
'napro-tercera-imagen.png'),

('Enalapril','C20H28N2O5','Presión arterial','30',635,
'ena-primera-imagen.png',
'ena-segunda-imagen.png',
'ena-tercera-imagen.png'),

('Cetirizina','C21H25ClN2O3','Alergias','20',68,
'ceti-primera-imagen.png',
'ceti-segunda-imagen.png',
'ceti-tercera-imagen.png');




INSERT INTO usuarios (documento, nombre, telefono, email, direccion, pin) VALUES
('123456789', 'Juan Perez', '3001234567', 'juan@gmail.com', 'Calle 1 #10-20', '1234');