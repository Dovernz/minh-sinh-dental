from booking.models import Article

class MarketingArticle(Article):
    class Meta:
        proxy = True
        verbose_name = 'Bài viết Marketing'
        verbose_name_plural = 'Bài viết Marketing'
