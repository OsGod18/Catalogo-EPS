CREATE DATABASE catalogo_eps;
USE catalogo_eps;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    direccion VARCHAR(150)
);

CREATE TABLE medicamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    formula_quimica VARCHAR(200),
    descripcion TEXT,
    cantidad INT
);

CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    medicamento_id INT,
    tipo_entrega VARCHAR(50),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);


INSERT INTO usuarios (documento,nombre,telefono,direccion)
VALUES
('1029988730','Dana Isabela Mendoza Diaz','313 4947422','Multifamiliares centauros'),
('40442736','Maria Isabel Diaz Alvarez','3112967896','Popular'),
('40396577','Nayiver Vanegas Ladino','3102192080','20 de julio'),
('17347417','Omar Yesid De la peña Muñoz','3115890972','La esperanza'),
('1019028888','Andres Felipe Velandia Guerrero','322 3281437','Las americas'),
('1144724438','Omar Stiven De la peña Vanegas','3023872857','Vereda Vanguardia'),
('40442736 ','Maria Isabel Diaz Alvarez ','3112967896','Barrio popular'),
('1121948552', 'Carlos Andrés Rojas Pardo', '310 5556789', 'Barrio El Estero'),
('52334412', 'Diana Marcela Torres', '322 4123344', 'La Esperanza 8va Etapa'),
('1018445670', 'Jorge Eliecer Ruiz', '320 8899001', 'Barrio San Benito'),
('40433221', 'Sandra Milena Castro', '311 2233445', 'Ciudad Porfía'),
('1122334455', 'Luis Alberto Moreno', '300 7654321', 'Urbanización Amarilo'),
('1005998877', 'Valentina Gómez Herrera', '302 1122334', 'Barrio El Buque'),
('30221445', 'Ricardo José Salcedo', '314 9988776', 'Barrio Barzal alto'),
('1110445566', 'Angie Natalia Perdomo', '310 4455667', 'Pinilla'),
('52889944', 'Marta Lucía Beltrán', '311 6677889', 'Barrio Santa Helena'),
('1020330440', 'Felipe Santiago Vargas', '322 3344556', 'Barrio Doce de Octubre');

INSERT INTO medicamentos (nombre,formula_quimica,descripcion,cantidad)
VALUES
('Amoxicilina', 'C16H19N3O5S', 'Antibiótico para infecciones bacterianas', 1030),
('Loratadina', 'C22H23ClN2O2', 'Antihistamínico para alergias', 332),
('Metformina', 'C4H11N5', 'Tratamiento para la diabetes tipo 2', 129),
('Omeprazol', 'C17H19N3O3S', 'Reductor de ácido gástrico', 400),
('Salbutamol', 'C13H21NO3', 'Broncodilatador para el asma', 950),
('Losartán', 'C22H22ClN6O', 'Tratamiento para la hipertensión', 1010),
('Atorvastatina', 'C33H35FN2O5', 'Para reducir el colesterol', 680),
('Insulina', 'C257H383N65O77S6', 'Hormona para el control de glucosa', 452),
('Diclofenaco', 'C14H11Cl2NO2', 'Analgésico y antiinflamatorio potente', 518),
('Naproxeno', 'C14H14O3', 'Alivio de dolores musculares e inflamación', 132),
('Enalapril', 'C20H28N2O5', 'Tratamiento para la presión arterial alta', 635),
('Cetirizina', 'C21H25ClN2O3', 'Antihistamínico para rinitis y urticaria', 68);

