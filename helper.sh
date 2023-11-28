function setup() {
  pip uninstall railfeed -y || true
  (cd src &&  python setup.py install)
}

function run() {
    export EMAIL='sureyasathiamoorthi@gmail.com' && export PASSWORD='#rrybU1RMcAS*mYr' && railfeed
}

