from flask import jsonify, g
from sqlalchemy_pagination import paginate

from config import DEFAULT_PER_PAGE


class PageParser:
    def __init__(self, request):
        self._base_url = request.base_url
        self.current_page = int(request.args.get('page[number]', 1))
        self.page_size = int(request.args.get('page[size]', DEFAULT_PER_PAGE))

    def link(self, page: int):
        return f"{self._base_url}?page[number]={page}&page[size]={self.page_size}"


class PaginatedResponse:
    def __init__(self, pager, paginator, schema):
        self.pager = pager
        self.paginator = paginator
        self.schema = schema

    def __call__(self, *args, **kwargs):
        items, _ = self.schema.dump(self.paginator.items)
        return jsonify(
            {
                'data': items,
                'links': {
                    'first': self.pager.link(1),
                    'last': self.pager.link(self.paginator.pages),
                    'prev': self.pager.link(self.paginator.previous_page) if self.paginator.has_previous else None,
                    'next': self.pager.link(self.paginator.next_page) if self.paginator.has_next else None
                },
                'meta': {
                    'total-pages': self.paginator.pages,
                    'total-items': self.paginator.total,
                    'current-page': self.pager.current_page,
                }
            }
        )


def api_list_response(request, model, schema):
    pager = PageParser(request)
    paginator = paginate(
        query=model.query.filter(model.company_id == g.user.company_id).order_by(model.created_at.desc()),
        page=pager.current_page,
        page_size=pager.page_size
    )
    return PaginatedResponse(pager, paginator, schema)()
