import json
from flask_restful import Resource
from data.model import repository as repo_model
from data.database import Repository, db_transaction
from utils import log_response
from flask import make_response
from flask_login import login_required
from singletons import workqueues


class DeleteApprRepositoriesTask(Resource):
    @log_response
    @login_required
    def delete(self):
        try:
            appr_repositories = Repository.select(Repository.id).where(Repository.kind == 2)
        except Repository.DoesNotExist:
            return make_response("No repositories found to delete", 404)
        except Exception as e:
            return make_response(
                json.dumps({"message": "Unable to find application kind repositories" + str(e)}), 500
            )

        try:
            with db_transaction():
                for r in appr_repositories:
                    repo_model.mark_repository_for_deletion(r.namespace_user, r.name, workqueues.namespace_gc_queue)
            return make_response("deleted", 200)
        except Exception as e:
            return make_response(
                json.dumps({"message": "Unable to delete application kind repositories" + str(e)}), 500
            )
