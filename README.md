# Comunicación Paramedico - Recepcionista
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Bonnish/comunicacion_paramedico_recepcionista)  
Proyecto académico desarrollado en **Django** (Python 3.13.7) que permite la comunicación entre un **paramédico** y el **recepcionista** de un hospital.  
El sistema está orientado a mejorar la coordinación en situaciones de emergencia, permitiendo registrar pacientes en camino, verificar información y derivarlos al área correspondiente.

---

## Tecnologías utilizadas

- **Python 3.13.7**
- **Django**
- **MySQL** (conector **PyMySQL**)
- **HTML** y **CSS** nativo para el front-end

---

## Funcionalidades principales

### Paramedico
- Registro de pacientes en camino a través de un formulario.
- Validación de datos con alertas en caso de error.
- Posibilidad de enviar una **derivación** al área correspondiente.

### Recepcionista
- Visualización de pacientes registrados en tiempo real.
- Cambio de estado del paciente (*en camino*, *recibido*, *atendido*).
- Acceso a un historial de acciones (registro, derivaciones, actualizaciones).

### Autenticación
- Sistema de **login y registro** de usuarios con distintos roles.
- Control de acceso a las vistas según el tipo de usuario (paramédico o recepcionista).

---

## Configuración de base de datos (MySQL)

1. Crear una base de datos MySQL:

   ```sql
   CREATE DATABASE comunicacion_hospital;
