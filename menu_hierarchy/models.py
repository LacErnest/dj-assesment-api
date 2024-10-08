import uuid
from django.db import models
from django.core.exceptions import ValidationError

class MenuItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    name = models.CharField(max_length=255, unique=True, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True, db_index=True)
    depth = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'depth']),
            models.Index(fields=['parent', 'depth']),
            models.Index(fields=['created_at', 'updated_at']),
        ]

    def clean(self):
        if MenuItem.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'A menu item with this name already exists.'})

    
    def update_children_depth(self):
        for child in self.children.all():
            child.depth = self.depth + 1
            child.save()

    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0
        super(MenuItem, self).save(*args, **kwargs)
        self.update_children_depth()
    
    def parent_name(self):
        return self.parent.name if self.parent else None

    parent_name.short_description = 'Parent Name'

    def __str__(self):
        return self.name