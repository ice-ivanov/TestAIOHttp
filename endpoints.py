import inspect
import json
from collections import OrderedDict

from aiohttp.http_exceptions import HttpBadRequest
from aiohttp.web import Request, Response
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from aiohttp.web_urldispatcher import UrlDispatcher

from models import Employee, Car, Part, session

__version__ = '0.1.0'


DEFAULT_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')


class RestEndpoint:
    def __init__(self):
        self.methods = {}

        for method_name in DEFAULT_METHODS:
            method = getattr(self, method_name.lower(), None)
            if method:
                self.register_method(method_name, method)

    def register_method(self, method_name, method):
        self.methods[method_name.upper()] = method

    async def dispatch(self, request: Request):
        method = self.methods.get(request.method.upper())
        if not method:
            raise HTTPMethodNotAllowed('', DEFAULT_METHODS)

        wanted_args = list(inspect.signature(method).parameters.keys())
        available_args = request.match_info.copy()
        available_args.update({'request': request})

        unsatisfied_args = set(wanted_args) - set(available_args.keys())
        if unsatisfied_args:
            # Expected match info that doesn't exist
            raise HttpBadRequest('')

        return await method(**{arg_name: available_args[arg_name] for arg_name in wanted_args})


class EmployeeEndpoint(RestEndpoint):
    """
    Employee API endpoint class
    """
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def response_200(self, response_data):
        print(response_data)
        for i in response_data:
            print(i)
        return Response(status=200, body=self.resource.encode({
            'employees': [
                {'id': emp.id,
                 'name': emp.name,
                 'surname': emp.surname,
                 'sex': emp.sex}
                for emp in response_data
            ]
        }), content_type='application/json')

    async def get(self, request) -> Response:
        query = request.rel_url.query
        instance = None

        if query.get('id'):
            id = query.get('id', '')
            instance = session.query(Employee).filter(Employee.id == id)
        if query.get('name'):
            name = query.get('name', '')
            instance = session.query(Employee).filter(Employee.name == name)
        if query.get('surname'):
            surname = query.get('surname', '')
            instance = session.query(Employee).filter(Employee.surname == surname)
        if query.get('sex'):
            sex = query.get('sex', '')
            instance = session.query(Employee).filter(Employee.sex == sex)
        if not instance:
            return await self.response_200(response_data=session.query(Employee))
        elif instance.count() == 0:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        else:
            return await self.response_200(response_data=instance)

    async def post(self, request):
        data = await request.post()
        employee = Employee(name=data.get('name'), surname=data.get('surname'), sex=data.get('sex'))
        session.add(employee)
        session.commit()

        return await self.response_200(response_data=session.query(Employee))

    async def put(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Employee).filter(Employee.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        emp = session.query(Employee).filter(Employee.id == id).first()

        emp.name = data.get('name')
        emp.surname = data.get('surname')
        emp.sex = data.get('sex')

        session.add(emp)
        session.commit()

        return await self.response_200(response_data=session.query(Employee))

    async def patch(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Employee).filter(Employee.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        emp = session.query(Employee).filter(Employee.id == id).first()

        emp.name = data.get('name') or emp.name
        emp.surname = data.get('surname') or emp.surname
        emp.sex = data.get('sex') or emp.sex

        return await self.response_200(response_data=session.query(Employee))

    async def delete(self, request):
        id = request.rel_url.query.get('id', '')
        employee = session.query(Employee).filter(Employee.id == id).first()
        if not employee:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        session.delete(employee)
        session.commit()
        return Response(status=204)


class CarEndpoint(RestEndpoint):
    """
    Car API endpoint class
    """
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def response_200(self, response_data):
        return Response(status=200, body=self.resource.encode({
            'cars': [
                {'id': car.id,
                 'model': car.model,
                 'year': car.year}
                for car in response_data
            ]
        }), content_type='application/json')

    async def get(self, request) -> Response:
        query = request.rel_url.query
        instance = None

        if query.get('id'):
            id = query.get('id', '')
            instance = session.query(Car).filter(Car.id == id)
        if query.get('model'):
            model = query.get('model', '')
            instance = session.query(Car).filter(Car.model == model)
        if query.get('year'):
            year = query.get('year', '')
            instance = session.query(Car).filter(Car.year == year)

        if not instance:
            return await self.response_200(response_data=session.query(Car))
        elif instance.count() == 0:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        else:
            return await self.response_200(response_data=instance)

    async def post(self, request):
        data = await request.post()
        car = Car(model=data.get('model'), year=data.get('year'))
        session.add(car)
        session.commit()

        return await self.response_200(response_data=session.query(Car))

    async def put(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Car).filter(Car.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        car = session.query(Car).filter(Car.id == id).first()

        car.model = data.get('model')
        car.year = data.get('year')

        session.add(car)
        session.commit()

        return await self.response_200(response_data=session.query(Car))

    async def patch(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Car).filter(Car.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        car = session.query(Car).filter(Car.id == id).first()

        car.model = data.get('model') or car.model
        car.year = data.get('year') or car.year

        return await self.response_200(response_data=session.query(Car))

    async def delete(self, request):
        id = request.rel_url.query.get('id', '')
        car = session.query(Car).filter(Car.id == id).first()
        if not car:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        session.delete(car)
        session.commit()
        return Response(status=204)


class PartEndpoint(RestEndpoint):
    """
    Part API endpoint class
    """
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def response_200(self, response_data):
        return Response(status=200, body=self.resource.encode({
            'parts': [
                {'id': part.id,
                 'name': part.name,
                 'country': part.country,
                 'model': part.model}
                for part in response_data
            ]
        }), content_type='application/json')

    async def get(self, request) -> Response:
        query = request.rel_url.query
        instance = None

        if query.get('id'):
            id = query.get('id', '')
            instance = session.query(Part).filter(Part.id == id)
        if query.get('name'):
            name = query.get('name', '')
            instance = session.query(Part).filter(Part.name == name)
        if query.get('country'):
            country = query.get('country', '')
            instance = session.query(Part).filter(Part.country == country)
        if query.get('model'):
            model = query.get('model', '')
            instance = session.query(Part).filter(Part.model == model)

        if not instance:
            return await self.response_200(response_data=session.query(Part))
        elif instance.count() == 0:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        else:
            return await self.response_200(response_data=instance)

    async def post(self, request):
        data = await request.post()
        part = Part(name=data.get('name'), country=data.get('country'), model=data.get('model'))
        session.add(part)
        session.commit()

        return await self.response_200(response_data=session.query(Part))

    async def put(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Part).filter(Part.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        emp = session.query(Part).filter(Part.id == id).first()

        emp.name = data.get('name')
        emp.country = data.get('country')
        emp.model = data.get('model')

        session.add(emp)
        session.commit()

        return await self.response_200(response_data=session.query(Part))

    async def patch(self, request):
        id = request.rel_url.query.get('id', '')
        if not session.query(Part).filter(Part.id == id).first():
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = await request.post()
        part = session.query(Part).filter(Part.id == id).first()

        part.name = data.get('name') or part.name
        part.country = data.get('country') or part.country
        part.model = data.get('model') or part.model

        return await self.response_200(response_data=session.query(Part))

    async def delete(self, request):
        id = request.rel_url.query.get('id', '')
        part = session.query(Part).filter(Part.id == id).first()
        if not part:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        session.delete(part)
        session.commit()
        return Response(status=204)


class RestResource:
    def __init__(self, employees, cars, parts, properties, id_field):
        self.employees = employees
        self.cars = cars
        self.parts = parts
        self.properties = properties
        # self.id_field = id_field

        self.employee_endpoint = EmployeeEndpoint(self)
        self.car_endpoint = CarEndpoint(self)
        self.part_endpoint = CarEndpoint(self)

    def register(self, router: UrlDispatcher):
        router.add_route('*', '/employees'.format(employees=self.employees), self.employee_endpoint.dispatch)
        router.add_route('*', '/cars'.format(cars=self.cars), self.car_endpoint.dispatch)
        router.add_route('*', '/parts'.format(parts=self.parts), self.part_endpoint.dispatch)

    def render(self, instance):
        return OrderedDict((data, getattr(instance, data)) for data in self.properties)

    @staticmethod
    def encode(data):
        return json.dumps(data, indent=4).encode('utf-8')

    def render_and_encode(self, instance):
        return self.encode(self.render(instance))
