from aiohttp.web import Application, run_app

from endpoints import RestResource
from models import Employee, Car, Part

employees = {}
cars = {}
parts = {}
app = Application()

emp_resource = RestResource('employee', Employee, employees, ('name', 'surname', 'sex'), 'name')
car_resource = RestResource('car', Car, cars, ('model', 'year'), 'model')
part_resource = RestResource('part', Part, parts, ('name', 'country', 'model'), 'name')

emp_resource.register(app.router)
car_resource.register(app.router)
part_resource.register(app.router)

if __name__ == '__main__':
    run_app(app)
