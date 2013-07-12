var app = angular.module('Gomoku', []);

// sock is SockJS object
function send(type, value) {
    sockjs.send(JSON.stringify({type: type, value: value}));
}

app.service('data', function() {
    var name = localStorage.name;
    this.state = {
        name: name,
        mode: 'start',
        games: [],
        playerCount: 0
    };
});

app.service('sock', function($rootScope) {
    var self = this;
    this.handlers = {};
    this.on = function(name, cb, ctx) {
        lst = self.handlers[name] || (this.handlers[name] = []);
        lst.push([cb, ctx]);
    };

    sockjs.onmessage = function(e) {
        console.log('message', e.data);
        var data = JSON.parse(e.data);

        var fns = self.handlers[data.type] || [];
        for (var i = 0, l = fns.length; i < l; i++) {
            fns[i][0].call(fns[i][1], data.value);
        }
        $rootScope.$digest();
    };
});

app.controller('App', function($scope, data, sock) {
    var state = $scope.state = data.state;

    sock.on('games', function(v) {
        state.games = v;
    });

    sock.on('players', function(v) {
        state.playerCount = v;
    });

    $scope.pageName = function() {
        return state.mode + '.html';
    };
});

app.controller('Start', function($scope, data, sock) {
    $scope.state = data.state;

    window.start = $scope;
    $scope.login = function() {
        if (!$scope.state.name) {
            return;
        }
        send('name', $scope.state.name);
    };

    sock.on('name:error', function(v) {
        $scope.error = v;
    });

    sock.on('name:success', function(v) {
        localStorage.name = $scope.state.name;
        $scope.state.mode = 'findgame';
    });

    $scope.$watch('state.name', function(v) {
        $scope.error = null;
    });
});

app.controller('FindGame', function($scope, data) {
    $scope.state = data.state;

    $scope.newGame = function() {
        send('new');
    };
});

app.controller('Info', function($scope, data) {
    $scope.state = data.state;

    window.info = $scope;
});
