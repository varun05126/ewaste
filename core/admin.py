from django.contrib import admin
from .models import PickupRequest, ContactMessage


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'short_address', 'has_location', 'created_at')
    list_filter   = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'address')
    readonly_fields = ('created_at',)
    ordering      = ('-created_at',)

    def has_location(self, obj):
        return "📍" if obj.latitude else "—"
    has_location.short_description = "Map"

    def short_address(self, obj):
        return obj.address[:60] + "…" if len(obj.address) > 60 else obj.address
    short_address.short_description = "Address"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'submitted_at', 'read')
    list_filter   = ('read', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('submitted_at',)
    actions       = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
        self.message_user(request, "Selected messages marked as read.")
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
        self.message_user(request, "Selected messages marked as unread.")
    mark_as_unread.short_description = "Mark selected as unread"
