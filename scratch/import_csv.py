import sys
import os
import csv

# Agregar la ruta del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from database.models import Empleado, Empresa, Sector

csv_path = 'C:\\Users\\Usuario\\Documents\\data-1783090660064.csv'

app = create_app()

with app.app_context():
    # Leer CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count_nuevos = 0
        count_existentes = 0
        
        for row in reader:
            nombre = row.get('Apellido y Nombre', '').strip()
            dni = row.get('DNI', '').strip()
            cuil = row.get('CUIL', '').strip()
            legajo = row.get('Legajo', '').strip()
            sector_nombre = row.get('Sector', '').strip()
            empresa_nombre = row.get('Empresa', '').strip()
            jornada_str = row.get('Jornada', '').strip()
            
            if not cuil or cuil.lower() in ('[null]', 'null', 'none'): cuil = None
            if not legajo or legajo.lower() in ('[null]', 'null', 'none'): legajo = None
            if not dni or dni.lower() in ('[null]', 'null', 'none'):
                continue # DNI es requerido
                
            # Buscar o crear empresa
            empresa = None
            if empresa_nombre:
                empresa = Empresa.query.filter_by(nombre=empresa_nombre).first()
                if not empresa:
                    empresa = Empresa(nombre=empresa_nombre)
                    db.session.add(empresa)
                    db.session.commit()
                    
            # Buscar o crear sector
            sector = None
            if sector_nombre:
                sector = Sector.query.filter_by(nombre=sector_nombre).first()
                if not sector:
                    sector = Sector(nombre=sector_nombre)
                    db.session.add(sector)
                    db.session.commit()
                    
            jornada_horas = 9.0
            try:
                jornada_horas = float(jornada_str)
            except:
                pass
                
            empleado = Empleado.query.filter_by(dni=dni).first()
            if not empleado:
                empleado = Empleado(
                    nombre_apellido=nombre,
                    dni=dni,
                    cuil=cuil,
                    legajo=legajo,
                    empresa_id=empresa.id if empresa else None,
                    sector_id=sector.id if sector else None,
                    jornada_horas=jornada_horas
                )
                db.session.add(empleado)
                count_nuevos += 1
            else:
                # Actualizar
                empleado.nombre_apellido = nombre
                if cuil: empleado.cuil = cuil
                if legajo: empleado.legajo = legajo
                if empresa: empleado.empresa_id = empresa.id
                if sector: empleado.sector_id = sector.id
                empleado.jornada_horas = jornada_horas
                count_existentes += 1
                
        db.session.commit()
        print(f"Importacion exitosa. Nuevos: {count_nuevos}, Actualizados: {count_existentes}")
