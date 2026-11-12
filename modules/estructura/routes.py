from flask import Blueprint, render_template, request
from flask_login import login_required

estructura_bp = Blueprint('estructura', __name__, url_prefix='/estructura')

# Fuente: “Diagrama organigrama 08-10-2026”. Es explícito para no inferir
# jerarquías desde sectores todavía incompletos de la nómina.
ORGANIGRAMA = {
    'direccion': {'cargo': 'Gerente General', 'nombre': 'Sol Alonso'},
    'operaciones': {'cargo': 'Gerente de Operaciones', 'nombre': 'Ignacio Diaz'},
    'areas': [
        {'nombre': 'Finanzas', 'icono': 'bi-cash-coin', 'color': 'gold', 'responsable': ('Gerente de Finanzas', 'Marcos Ciaramitaro'), 'equipos': [
            ('Analista de Tesorería', ['Adrian Pamelin']), ('Administración general', ['Arancibia Emanuel']), ('Auditor interno', ['Armando Viani'])]},
        {'nombre': 'Contabilidad y BI', 'icono': 'bi-bar-chart-line', 'color': 'violet', 'responsable': ('Gerente de Contabilidad', 'Patricia Nicastro'), 'equipos': [
            ('Líder de Costo y BI', ['Diana Subia']), ('Equipo contable', ['Jorgelina Tonelli', 'Doris Barañao'])]},
        {'nombre': 'Supply Chain', 'icono': 'bi-box-seam', 'color': 'orange', 'responsable': ('Gerente Supply Chain', 'Damian Díaz'), 'equipos': [
            ('Responsable de Almacén', ['Jose Agricolo', 'Mauro Ticona']), ('Mantenimiento vehicular', ['Adrian Tello']), ('Operación de almacén', ['Miguel Monte']), ('Compras', ['Gabriel Dominguez'])]},
        {'nombre': 'Comercial', 'icono': 'bi-graph-up-arrow', 'color': 'blue', 'responsable': ('Gerente Comercial Nacional', 'Juan Ignacio Distefano'), 'equipos': [
            ('Canal Supermercados · Jorge Guillen', ['Carina Marzola', 'Guillermo Bean', 'Veronica Llaneza', 'Maximiliano Gagliano']),
            ('Canal Distribuidores · Manuel Castillo', ['Emiliano Calle', 'Fabián Cordoba', 'Martin Artigas', 'Eduardo Juarez', 'Pablo Castro', 'Gerardo Morales']),
            ('Canal Minorista · Miguel Barbero', ['Julio Peralta', 'Martin Pereira', 'Angel Corales', 'Ruben Reynoso']), ('Facturación', ['Roberto Albornoz'])]},
        {'nombre': 'Producción', 'icono': 'bi-gear-wide-connected', 'color': 'red', 'responsable': ('Gerente de Producción', 'Daniel Diaz'), 'equipos': [
            ('Líder de Producción · Matias Barroso', []), ('Supervisores de Producción', ['Marcelo Paez', 'Jorge Sotelo', 'Juan Sevilla', 'Darío Azzolina']), ('Supervisor de Soplado', ['Fabian Barraquero']),
            ('Operarios de Producción', ['Leandro Salinas', 'Carlos Garcia', 'Aldo Antonucci', 'Gaston Montiel', 'Danilo Lopez', 'Eduardo Albornoz', 'Santiago Borquez', 'Andres Sosa', 'Alejo Gauna', 'Alexander Gutierrez', 'Juan Escobar', 'Ernesto Gonzalez', 'Franco Lopez', 'Martin Sanchez', 'Felix Campillay']),
            ('Operarios de Soplado', ['Marcelo Rosales', 'Juan Soria', 'Marcelo Carbone', 'Miguel Avila', 'Cristian Calderon', 'Jose Quiroga', 'Walter Aguilera'])]},
        {'nombre': 'Mantenimiento', 'icono': 'bi-tools', 'color': 'slate', 'responsable': ('Líder de Mantenimiento', 'Juan Pablo Longhin'), 'equipos': [
            ('Operarios de Mantenimiento', ['Ricardo Zamora', 'Gustavo Muñoz', 'Hector Funes', 'Sebastian Pinti', 'Eduardo Mendoza', 'Gaspar Coria', 'Cristian Bertinatto', 'Roberto Videla', 'Zanabria Lucas'])]},
        {'nombre': 'Recursos Humanos', 'icono': 'bi-people', 'color': 'pink', 'responsable': ('Gerente de RR. HH.', 'Luciana Liguori'), 'equipos': [
            ('Analista Junior', ['Romina Subia']), ('Administración de RR. HH.', ['Andrea Alonso'])]},
        {'nombre': 'Logística y Expedición', 'icono': 'bi-truck', 'color': 'green', 'responsable': ('Líder de Logística y Expedición', 'Ariel Garro'), 'equipos': [
            ('Responsable de Expedición', ['Carlos Bagnardi']), ('Choferes de larga distancia', ['Alberto Olguin', 'Franco Mahona', 'Carlos Motta', 'Carlos Lescano']), ('Operarios de Expedición', ['Nestor Marin', 'Mauricio Montenegro', 'Nicolas Di Batista', 'Emiliano Flores', 'Facundo Gini'])]},
        {'nombre': 'Calidad, Seguridad y Tecnología', 'icono': 'bi-shield-check', 'color': 'cyan', 'responsable': ('Líder de Calidad y Jarabe', 'Agustin Rodriguez'), 'equipos': [
            ('Higiene y Seguridad · Celeste Rosales', []), ('Calidad y Jarabe', ['Dario Alonso', 'Luis Moya', 'Renna Juan', 'Juan Amaya', 'Gustavo Funes', 'Carlos Videla', 'Carlos Abrego', 'Mauro Diaz']),
            ('Sistemas · Daniel Rinaldi', ['Giuliana Bonora', 'Adriano Rovelli']), ('Legales', [])]},
    ],
}

def _area_coincide(area, termino):
    textos = [area['nombre'], *area['responsable']]
    for titulo, personas in area['equipos']:
        textos.extend([titulo, *personas])
    return termino in ' '.join(textos).casefold()

@estructura_bp.route('/')
@login_required
def index():
    busqueda = request.args.get('q', '').strip()
    areas = ORGANIGRAMA['areas']
    if busqueda:
        areas = [area for area in areas if _area_coincide(area, busqueda.casefold())]
    personas = {ORGANIGRAMA['direccion']['nombre'], ORGANIGRAMA['operaciones']['nombre']}
    for area in ORGANIGRAMA['areas']:
        personas.add(area['responsable'][1])
        for _, integrantes in area['equipos']:
            personas.update(integrantes)
    return render_template('estructura/index.html', organigrama=ORGANIGRAMA, areas=areas,
                           busqueda=busqueda, total_personas=len(personas), resultados=len(areas))
