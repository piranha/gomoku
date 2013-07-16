var app = angular.module('Gomoku', []);

// sock is SockJS object
function send(type, value) {
    sockjs.send(JSON.stringify({type: type, value: value}));
}

function parseField(src) {
    return src.split('\n').map(function(line) {
        return Array.prototype.map.call(line,
                                        function(x) { return x; });
    });
}

app.service('data', function($rootScope) {
    var name = localStorage.name;
    var state = this.state = {
        name: name,
        mode: 'login',
        games: [],
        current: null,
        playerCount: 0,
        openGame: function(game) {
            state.current = game;
            state.mode = 'game';
            $rootScope.$broadcast('game-update');
        }
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
    window.state = state;

    sock.on('games', function(v) {
        state.games = v;
    });

    sock.on('players', function(v) {
        state.playerCount = v;
    });

    sock.on('game', function(g) {
        if (state.mode == 'findgame' || state.mode == 'game') {
            state.openGame(g);
        }
    });

    sock.on('open', function(g) {
        data.state.openGame(g);
    });

    $scope.pageName = function() {
        return state.mode + '.html';
    };
});

app.controller('Login', function($scope, data, sock) {
    $scope.state = data.state;

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

    if ($scope.state.name) {
        $scope.login();
    }
});

app.controller('FindGame', function($scope, data) {
    $scope.state = data.state;

    $scope.join = function(id) {
        send('join', id);
    };
});

app.controller('NewGame', function($scope) {
    $scope.size = 15;
    $scope.inarow = 5;
    $scope.second = false;

    $scope.newGame = function() {
        send('new', {size: $scope.size,
                     inarow: $scope.inarow,
                     second: $scope.second});
    };

});

app.controller('Info', function($scope, data) {
    $scope.state = data.state;

    $scope.myGames = $scope.state.games.filter(function(g) {
        return g.player1 == data.state.name || g.player2 == data.state.name;
    });

    $scope.open = function(id) {
        send('open', id);
    };

    $scope.toGameFinder = function() {
        data.state.mode = 'findgame';
    };

    $scope.logout = function() {
        data.state.name = '';
        data.state.mode = 'login';
        send('name', null);
    };
});

app.controller('Game', function($scope, data, sock) {
    $scope.state = data.state;
    function updateState() {
        $scope.game = data.state.current;
        $scope.field = parseField($scope.game.field);
        $scope.symbol = $scope.game.player1 == state.name ? 'x' : 'o';
        $scope.myTurn = $scope.game.player1 == state.name ^
            $scope.game.eventurn;
        $scope.lastTurn = null;
    }
    $scope.$on('game-update', updateState);
    updateState();

    $scope.nbspMaybe = function(c) {
        return c === ' ' ? '&nbsp;' : c;
    };

    $scope.put = function(x, y) {
        if ($scope.game.done)
            return;
        if (!$scope.myTurn)
            return;
        if ($scope.lastTurn) // do nothing until last turn is approved
            return;
        if ($scope.field[x][y] !== ' ')
            return;
        $scope.field[x][y] = $scope.symbol;
        $scope.lastTurn = [x, y];
        $scope.game.eventurn = !$scope.game.eventurn;
        send('turn', [$scope.game.id, [x, y]]);
    };

    sock.on('turn:error', function() {
        if (!$scope.lastTurn)
            return;
        $scope.field[$scope.lastTurn[0]][$scope.lastTurn[1]] = ' ';
        $scope.lastTurn = null;
        $scope.game.eventurn = !$scope.game.eventurn;
    });

    sock.on('turn:success', function() {
        $scope.lastTurn = null;
    });
});
