import os
import json
import datetime

import flask
from flask import request
from werkzeug import exceptions

import github_quality
import config
import l0_repo

app = flask.Flask(__name__)

app.jinja_env.variable_start_string = '((('
app.jinja_env.variable_end_string = ')))'
app.comment_start_string = '((#'
app.comment_end_string = '#))'

mean_stars_per_issue = l0_repo.get_mean_stars_per_issue()

repo_lists = {
    'connect_middleware': set([
        'expressjs/body-parser',
        'Raynos/body',
        'cojs/co-body',
        'stream-utils/raw-body',
        'expressjs/compression',
        'expressjs/timeout',
        'expressjs/cookie-parser',
        'expressjs/cookie-session',
        'expressjs/csurf',
        'expressjs/errorhandler',
        'expressjs/session',
        'expressjs/method-override',
        'expressjs/morgan',
        'expressjs/response-time',
        'expressjs/serve-favicon',
        'expressjs/serve-index',
        'expressjs/serve-static',
        'expressjs/vhost',
        'pillarjs/cookies',
        'expressjs/keygrip',
        'stream-utils/raw-body',
        'andrewrk/connect-multiparty',
        'mscdex/connect-busboy',
        'ljharb/qs',
        'isaacs/st',
        'andrewrk/connect-static',
        "aaronblohowiak/routes.js",
        "Raynos/routes-router",
        "saambarati/mapleTree",
        "Raynos/http-methods",
        "isaacbw/node-egress",
        "stream-utils/raw-body",
        "jed/cookies",
        "jed/keygrip",
        "Raynos/send-data",
        "Raynos/redirecter",
        "expressjs/serve-favicon",
        "ghostsnstuff/serve-file-download",
        "isaacs/st",
        "Raynos/serve-browserify",
        "Raynos/npm-less",
        "mikeal/filed",
        "mikeal/request",
        "dominictarr/hyperscript",
        "visionmedia/consolidate.js/",
        "raynos/validate-form",
        "spumko/joi",
        "mafintosh/is-my-json-valid",
        "isaacs/redsess",
        "rvagg/level-session",
        "rvagg/node-generic-session",
        "dominictarr/config-chain",
        "Raynos/static-config",
        "Raynos/error",
        "rvagg/bole",
    ]),
    'node_sql': [
        'dresende/node-orm2',
        'tgriesser/bookshelf',
        'felixge/node-mysql',
        '1602/jugglingdb',
        'brianc/node-postgres',
        'tgriesser/knex',
        'balderdashy/waterline',
        'sequelize/sequelize',
        'devinivy/dogwater'
    ],
    'python_unit_testing': [
        'rlisagor/freshen',
        'gabrielfalcao/sure',
        'gabrielfalcao/lettuce',
        'behave/behave',
        'nose-devs/nose2',
        'nose-devs/nose',
        'pytest-dev/pytest'
    ],
    'web_frameworks': [
        'meteor/meteor',
        'mitsuhiko/flask',
        'rails/rails',
        'django/django',
        'phoenixframework/phoenix',
        'balderdashy/sails',
        'strongloop/express',
        'nodejs/node',
        'senchalabs/connect',
        'hapijs/hapi',
        'laravel/laravel',
        'symfony/symfony',
        'linnovate/mean',
        'revel/revel',
        'cakephp/cakephp',
        'derbyjs/derby',
        'padrino/padrino-framework',
        'hanami/hanami',
        'keithwhor/nodal',
        'kraih/mojo',
        'ninjaframework/ninja',
        'web2py/web2py',
        'pakyow/pakyow',
        'perl-catalyst/catalyst-runtime',
    ],
    'front_end_frameworks': [
        'angular/angular',
        'facebook/react',
        'facebook/flux',
        'angular/angular.js',
        'jashkenas/backbone',
        'vuejs/vue',
        'jquery/jquery',
        'emberjs/ember.js',
        'lhorie/mithril.js',
        'Polymer/polymer',
        'riot/riot'
    ],
    'vue_state': [
        'visionmedia/superagent',
        'vuejs/vuex',
        'reactjs/redux',
        'egoist/revue',
        'vuejs/vue-resource'
    ],
    'programming_languages': [
        'Microsoft/dotnet',
        'apple/swift',
        'rust-lang/rust',
        'golang/go',
        'jashkenas/coffeescript',
        'ruby/ruby',
        'php/php-src',
        'JuliaLang/julia',
        'elixir-lang/elixir',
        'scala/scala',
        'clojure/clojure',
        'dotnet/roslyn',
        'erlang/otp',
        'JetBrains/kotlin',
        'nim-lang/Nim',
        'elm-lang/elm-compiler',
        'purescript/purescript',
        'timburks/nu',
        'Frege/frege',
        'gkz/LiveScript',
        'stevedekorte/io',
        'groovy/groovy-core',
        'racket/racket',
        'HaxeFoundation/haxe',
        'D-Programming-Language/dmd',
        'fsharp/fsharp',
        'eholk/harlan',
        'red/red',
        'amber-smalltalk/amber',
        'ocaml/ocaml',
        'dart-lang/sdk',
        'dylan-lang/opendylan',
        'chapel-lang/chapel',
    ],
    'git_guis': [
        'pieter/gitx',
        'rowanj/gitx',
        'brotherbard/gitx',
        'laullon/gitx',
        'beheadedmyway/gity',
        'andreberg/gitx'
    ],
    'databases': [
        'google/leveldb',
        'mongodb/mongo',
        'neo4j/neo4j',
        'antirez/redis',
        'rethinkdb/rethinkdb',
        'pouchdb/pouchdb',
        'thinkaurelius/titan',
    ],
    'python_rpc': [
        'shibukawa/curl_as_dsl',
        'irmen/Pyro4',
        'tomerfiliba/rpyc',
        'arskom/spyne',
        'python-symmetric-jsonrpc',
        'dwb/jsonrpc2-zeromq-python',
        'kiorky/SOAPpy',
        'wamp-proto/wamp-proto',
        'geoffwatts/zmqrpc',
        '0rpc/zerorpc-python',
    ],
    'hundred_best': [
        'lodash/lodash',
        'jlmakes/scrollreveal.js',
        'carhartl/jquery-cookie',
        'qrohlf/trianglify',
        'tobiasahlin/SpinKit',
        'Alamofire/Alamofire',
        'jwagner/smartcrop.js',
        'roots/sage',
        'SnapKit/Masonry',
        'phanan/htaccess',
        'senchalabs/connect',
        'Famous/famous',
        'postcss/autoprefixer',
        'zenorocha/clipboard.js',
        'facebook/Shimmer',
        'sindresorhus/quick-look-plugins',
        'afaqurk/linux-dash',
        'twbs/bootstrap-sass',
        'daneden/animate.css',
        'briangonzalez/jquery.adaptive-backgrounds.js',
        'nodemailer/nodemailer',
        'zxing/zxing',
        'github/fetch',
        'wycats/handlebars.js',
        'PredictionIO/PredictionIO',
        'keen/dashboards',
        'fullstackio/FlappySwift',
        'douglascrockford/JSON-js',
        'NARKOZ/hacker-scripts',
        'vuejs/vue',
        'rackt/react-router',
        'IanLunn/Hover',
        'yeoman/yeoman',
        'FezVrasta/bootstrap-material-design',
        'Flipboard/FLEX',
        'scottjehl/picturefill',
        'greatfire/wiki',
        'hapijs/hapi',
        'HannahMitt/HomeMirror',
        'bevacqua/dragula',
        'facebook/pop',
        'phoenixframework/phoenix',
        'jquery/jquery',
        'petkaantonov/bluebird',
        'yudai/gotty',
        'gulpjs/gulp',
        'AFNetworking/AFNetworking',
        'sindresorhus/pageres',
        'jashkenas/backbone',
        'designmodo/Flat-UI',
        'plataformatec/devise',
        'Microsoft/dotnet',
        'onevcat/VVDocumenter-Xcode',
        'astaxie/build-web-application-with-golang',
        'facebook/flux',
        'resume/resume.github.com',
        'rbenv/rbenv',
        'sbstjn/timesheet.js',
        'h5bp/Effeckt.css',
        'google/web-starter-kit',
        'desandro/masonry',
        'mperham/sidekiq',
        'basecamp/trix',
        'harthur/brain',
        'go-martini/martini',
        'thoughtbot/bourbon',
        'dokku/dokku',
        'yaronn/blessed-contrib',
        'tpope/vim-pathogen',
        'ejci/favico.js',
        'wg/wrk',
        'square/retrofit',
        'balderdashy/sails',
        'google/iosched',
        'amazeui/amazeui',
        'jessepollak/card',
        'WickyNilliams/headroom.js',
        'caolan/async',
        'mailcheck/mailcheck',
        'enaqx/awesome-react',
        'facebook/osquery',
        'imakewebthings/waypoints',
        'purifycss/purifycss',
        'FreeCodeCamp/FreeCodeCamp',
        'typicode/json-server',
        'flightjs/flight',
        'marmelab/gremlins.js',
        'jashkenas/underscore',
        'joewalnes/websocketd',
        'rackt/redux',
        'postcss/postcss',
        'Thibaut/devdocs',
        'strongloop/express',
        'guzzle/guzzle',
        'nvbn/thefuck',
        'twbs/bootstrap',
        'limetext/lime',
        'koajs/koa',
        'davatron5000/FitText.js',
        'isagalaev/highlight.js'
    ],
    'hapi_plugins': [
        'franciscogouveia/hapi-rbac',
        'toymachiner62/hapi-authorization',
        'hapijs/bell',
        'codedoctor/hapi-auth-anonymous',
        'hapijs/hapi-auth-basic',
        'Salesflare/hapi-auth-bearer-simple',
        'johnbrett/hapi-auth-bearer-token',
        'hapijs/hapi-auth-cookie',
        'asafdav/hapi-auth-extra',
        'hapijs/hapi-auth-hawk',
        'ryanfitz/hapi-auth-jwt',
        '58bits/hapi-auth-signature',
        'molekilla/hapi-passport-saml',
        'Mkoopajr/hapi-session-mongo',
        'glennjones/hapi-swagger',
        'codeandfury/node-hapi-swagger-models',
        'z0mt3c/hapi-swaggered',
        'z0mt3c/hapi-swaggered-ui',
        'hapijs/lout',
        'codeva/hapi-i18n',
        'maxnachlinger/hapi-l10n-gettext',
        'gpierret/hapi18n',
        'opentable/hapi-accept-language',
        'ozum/hapi-locale',
        'Wayfarer247/airbrake-hapi',
        'danielb2/blipp',
        'hapijs/good',
        'mac-/hapi-statsd',
        'idosh/hapi-alive',
        'aduis/hapi-rabbit',
        'mtharrison/susie',
        'nlf/blankie',
        'hapijs/crumb',
        'btmorex/hapi-server-session',
        'hapijs/yar',
        'mikefrey/hapi-dust',
        'gergoerdosi/hapi-json-view',
        'landau/hapi-react',
        'jedireza/hapi-react-views',
        'tanepiper/quorra',
        'watchup/hapi-mongoose',
        'hapijs/bassmaster',
        'devinivy/bedwetter',
        'g-div/crudy',
        'devinivy/dogwater',
        'nathanbuchar/hapi-glee',
        'bleupen/halacious',
        'sigfox/hapi-algolia-search',
        'poeticninja/hapi-assets',
        'ide/hapi-async-handler',
        'lob/hapi-bookshelf-models',
        'lob/hapi-bookshelf-serializer',
        'brainsiq/hapi-boom-decorators',
        'poeticninja/hapi-cache-buster',
        'gergoerdosi/hapi-cloudinary-connector',
        'AdrieanKhisbe/configue',
        'knownasilya/hapi-decorators',
        'christophercliff/hapi-dropbox-webhooks',
        'briandela/hapi-heroku-helpers',
        'danielb2/hapi-info',
        'sibartlett/hapi-io',
        'maxnachlinger/hapi-level-db',
        'ruiquelhas/hapi-magic-filter',
        'gergoerdosi/hapi-mailer',
        'jedireza/hapi-mongo-models',
        'codedoctor/hapi-mongoose-db-connector',
        'poeticninja/hapi-named-routes',
        'Pranay92/hapi-next',
        'jedireza/hapi-node-postgres',
        'christophercliff/hapi-nudge',
        'caligone/hapio',
        'developmentseed/hapi-paginate',
        'fknop/hapi-pagination',
        'sandfox/node-hapi-redis',
        'developmentseed/hapi-response-meta',
        'clarkie/hapi-route-directory',
        'bsiddiqui/hapi-router',
        'codedoctor/hapi-routes-status',
        'codeandfury/node-hapi-sequelize',
        'danecando/hapi-sequelized',
        'viniciusbo/hapi-suricate',
        'mtharrison/hapi-to',
        'christophercliff/hapi-webpack',
        'atroo/hapi-webpack-dev-server-plugin',
        'mark-bradshaw/mrhorse',
        'dschenkelman/patova',
        'hapijs/poop',
        'hapijs/reptile',
        'walmartlabs/ridicule',
        'hapijs/scooter',
        'continuationlabs/tacky',
        'briandela/therealyou',
        'smaxwellstewart/toothache',
        'vdeturckheim/tournesol',
        'hapijs/tv',
        'cristobal151/hapi-recaptcha',
        'ruiquelhas/blaine',
        'ruiquelhas/burton',
        'ruiquelhas/copperfield',
        'ruiquelhas/coutts',
        'ruiquelhas/fischbacher',
        'ruiquelhas/henning',
        'ruiquelhas/houdin',
        'ruiquelhas/lafayette',
        'ruiquelhas/supervizor',
        'ruiquelhas/thurston',
        'mac-/ratify',
        'hapijs/boom',
        'hapijs/confidence',
        'hapijs/faketoe',
        'hapijs/glue',
        'hapijs/h2o2',
        'hapijs/hoek',
        'hapijs/inert',
        'hapijs/joi',
        'hapijs/kilt',
        'hapijs/lab',
        'hapijs/makemehapi',
        'hapijs/nes',
        'hapijs/qs',
        'hapijs/rejoice',
        'hapijs/shot',
        'hapijs/topo',
        'hapijs/vision',
        'hapijs/wreck'
    ]
}


@app.route('/')
def index():
    print 'lists:', repo_lists
    return flask.render_template('index.html', repo_lists=repo_lists)


def get_repo(repo_path):
    repo_dict = github_quality.pull_repo(repo_path, mean_stars_per_issue, auth=config.auth_)
    return {k: repo_dict[k] for k in (
        'full_name', 'score', 'has_issues', 'rating_str', 'explanation', 'open_issues',
        'stargazers_count', 'age', 'closed_issues') if k in repo_dict}


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.days
        else:
            return super(DateTimeEncoder, self).default(obj)


@app.route('/templates/<path:path>')
def send_js(path):
    return flask.send_from_directory('templates', path)


@app.route('/<username>/<repo_name>')
@app.route('/<username>/<repo_name>/')
def query_repo(username, repo_name):
    repo_dict = get_repo('/'.join((username, repo_name)))
    repo_json = DateTimeEncoder().encode(repo_dict)
    return flask.render_template('repo.html', repo_json=repo_json)


@app.route('/lists/<list_name>')
def query_list(list_name):
    paths = repo_lists[list_name] if list_name in repo_lists else None
    if paths:
        repos = []
        for path in paths:
            try:
                repos.append(get_repo(path))
            except exceptions.NotFound:
                pass
        list_json = DateTimeEncoder().encode(sorted(repos, key=lambda r: -r['score']))
        return flask.render_template('list.html', list_json=list_json)
    abort(404)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', True))
