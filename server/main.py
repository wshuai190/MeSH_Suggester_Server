from flask import Flask, jsonify, request
from waitress import serve
from suggest_mesh_terms import Suggest_MeSH_Terms_With_BERT, prepare_model
from suggest_with_other import ATM_MeSH_Suggestion, MetaMap_MeSH_Suggestion, UMLS_MeSH_Suggestion
app = Flask(__name__)


def get_mesh_suggestions(params):
    BERT_Suggest = Suggest_MeSH_Terms_With_BERT(params)
    return BERT_Suggest.suggest()


def get_other_mesh_suggestion(params):
    if params['payload']['Type'] == 'ATM':
        ATM = ATM_MeSH_Suggestion(params)
        return ATM.suggest()
    elif params['payload']['Type'] == 'UMLS':
        UMLS = UMLS_MeSH_Suggestion(params)
        return UMLS.suggest()
    elif params['payload']['Type'] == 'MetaMap':
        MetaMap = MetaMap_MeSH_Suggestion(params)
        return MetaMap.suggest()


@app.route("/api/v1/resources/mesh", methods=['GET'])
def get_mesh():
    terms = request.args.get("term")
    split_terms = terms.split("$")
    type = request.args.get("type")
    payload = {
        "Keywords": split_terms,
        "Type": type
    }
    if type in ['Semantic', 'Atomic', 'Fragment']:
        params = {
            "payload": payload,
            "mesh_dict": mesh_dict,
            "model": model,
            "tokenizer": tokenizer,
            "retriever": retriever,
            "look_up": look_up,
            "model_w2v": model_w2v
        }
        response = get_mesh_suggestions(params)
    else:
        params = {
            "payload": payload
        }
        response = get_other_mesh_suggestion(params)

    formatted_response = {
        "Splits": split_terms,
        "Data": response
    }
    response = jsonify(formatted_response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The Resource You Requested Is Not Found.</p>", 404


if __name__ == '__main__':
    mesh_dict, model, tokenizer, retriever, look_up, model_w2v = prepare_model()
    # app.run()
    serve(app, host='127.0.0.1', port=5000)
