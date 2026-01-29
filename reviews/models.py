from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from directory.models import Business

class Review(models.Model):
    """تقييمات المحلات"""
    business = models.ForeignKey(
        Business, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name='المحل'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        default=1,
        verbose_name='المستخدم'
    )
    rating = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='التعليق'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='موافق عليه'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        ordering = ['-created_at']
        unique_together = ['business', 'user']  # ← ده مهم!
        indexes = [
            models.Index(fields=['business', 'is_approved']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        if self.user:
            return f'{self.user.get_full_name() or self.user.username} - {self.business.name} ({self.rating}★)'
        return f'تقييم - {self.business.name} ({self.rating}★)'
    
    @property
    def reviewer_name(self):
        """اسم المراجع"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return 'مجهول'
