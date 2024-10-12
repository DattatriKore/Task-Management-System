from rest_framework.permissions import BasePermission

# Admin And Manager Permission Class
class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'Admin' or request.user.role == 'Manager')

# Admin Permission Class
class IsAdmin(BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and request.user.role == 'Admin'
    
# Manager Permission Class
class IsManager(BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and request.user.role == 'Manager'
    
# Employee Permission Class
class IsEmployee(BasePermission):
    def has_permission(self,request,view):
        return request.user.is_authenticated and request.user.role == 'Employee'
    
# class IsAdminOrManagerUser(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user