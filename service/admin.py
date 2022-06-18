from django.contrib import admin

from .models import JobPost, Milestone ,MilestoneFiles

class JobPostAdmin(admin.ModelAdmin):
    list_display = ('client', 'manager', 'active', 'date_requested', 'price_paid',
                    'paid_for',)
    ordering = ['-active',  '-date_requested', '-paid_for', '-price_paid']

    def get_queryset(self, request):
        qs = super(JobPostAdmin, self).get_queryset(request)
        # qs = qs.order_by('-date_requested')
        return qs.order_by(*self.ordering)


admin.site.register(JobPost, JobPostAdmin)

admin.site.register(Milestone)
admin.site.register(MilestoneFiles)
