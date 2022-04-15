from django.contrib import admin
from .models import ManagerEvaluation, ManagerPreference


class ManagerEvaluationAdmin(admin.ModelAdmin):
    list_display = ('manager', 'accepted', 'evaluation_completed',)
    ordering = ['-accepted', '-evaluation_completed']

    def get_queryset(self, request):
        qs = super(ManagerEvaluationAdmin, self).get_queryset(request)
        # qs = qs.order_by('-date_requested')
        return qs.order_by(*self.ordering)


admin.site.register(ManagerEvaluation, ManagerEvaluationAdmin)
# admin.site.register(ManagerBiases)
admin.site.register(ManagerPreference)
