from flask import jsonify, request
from app.services.employee_service import EmployeeService

class EmployeeController:
    @staticmethod
    def get_all_employees():
        employees = EmployeeService.get_all_employees()
        return jsonify([employee.to_dict() for employee in employees]), 200
    
    @staticmethod
    def get_employees_by_company(company_id):
        employees = EmployeeService.get_employees_by_company(company_id)
        return jsonify([employee.to_dict() for employee in employees]), 200
    
    @staticmethod
    def get_employee_by_id(employee_id):
        employee = EmployeeService.get_employee_by_id(employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        return jsonify(employee.to_dict()), 200
    
    @staticmethod
    def create_employee():
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'email', 'cpf', 'salary', 'company_id', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        employee, error = EmployeeService.create_employee(data)
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(employee.to_dict()), 201
    
    @staticmethod
    def update_employee(employee_id):
        data = request.get_json()
        employee, error = EmployeeService.update_employee(employee_id, data)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify(employee.to_dict()), 200
    
    @staticmethod
    def delete_employee(employee_id):
        success, error = EmployeeService.delete_employee(employee_id)
        
        if not success:
            return jsonify({"error": error}), 404
        
        return jsonify({"message": "Employee deleted successfully"}), 200
