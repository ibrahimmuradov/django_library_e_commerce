
class Uploader:
    @staticmethod
    def upload_image_author(objName, filename):
        return f"author/{objName.username}/{filename}"

    @staticmethod
    def upload_image_user(objName, filename):
        return f"user/{objName.username}/{filename}"

    @staticmethod
    def upload_image_book(objName, filename):
        return f"book/{objName.book.slug}/{filename}"

    @staticmethod
    def upload_image_blog(objName, filename):
        return f"blog/{objName.title}/{filename}"