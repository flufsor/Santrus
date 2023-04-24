import glob
import shutil
import frontmatter
import mistune
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

NAME = "John Doe"
PERSONALDETAILS = {
    "email": "john@doe.com",
    "address": " 3542 Berry Street · Cheyenne Wells, CO 80810 · (317) 585-8468 ·",
}
BLOG_ORDER = 1.2

env = Environment(
    loader=FileSystemLoader("templates"),
)


class Page():
    def __init__(self, title, order, template, content):
        self.title = title
        self.order = order
        self.template = template
        self.content = content
        self.slug = slugify(title)


class Post():
    def __init__(self, title, date, tags, content):
        self.title = title
        self.date = date
        self.tags = tags
        self.content = content
        self.slug = slugify(title)


def get_pages():
    pages = []
    for page in glob.glob("pages/*.md"):
        with open(page, "r") as page_file:
            obj = frontmatter.load(page_file)
            html = mistune.html(obj.content)
            pages.append(Page(obj["title"], obj["order"], obj["template"], html))
    pages[0].slug = "index"
    pages.append(Page("Blog", BLOG_ORDER, "blog", None))
    return sorted(pages, key=lambda x: getattr(x, "order"))


def get_posts_tags():
    posts = []
    tags = []
    for post in glob.glob("posts/*.md"):
        with open(post, "r") as post_file:
            obj = frontmatter.load(post_file)
            html = mistune.html(obj.content)
            for tag in obj["tags"]:
                if tag not in tags:
                    tags.append(tag)
            posts.append(Post(obj["title"], obj["date"], obj["tags"], html))
    return sorted(posts, key=lambda x: getattr(x, "date"), reverse=True), tags


def render_pages():
    pages = get_pages()
    for page in pages:
        template = env.get_template(f"{page.template}.html")
        with open(f"docs/{page.slug}.html", "w") as out:
            out.write(template.render(name=NAME, personal=PERSONALDETAILS, navigation=pages, title=page.title,
                                      content=page.content))


def render_blog(filtered_tags=None):
    posts, tags = get_posts_tags()
    if filtered_tags:
        for post in posts:
            if not set(filtered_tags).issubset(set(post.tags)):
                posts.remove(post)
    pages = get_pages()
    template = env.get_template("blog.html")
    with open(f"docs/blog.html", "w") as out:
        out.write(template.render(navigation=pages, tags=tags, posts=posts))


def copy_assets():
    shutil.copytree('./assets', 'docs/', dirs_exist_ok=True)


if __name__ == "__main__":
    copy_assets()
    render_pages()
    render_blog()
