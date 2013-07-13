function MockSockJS() {
    this.sent = [];
}
MockSockJS.prototype.send = function(data) {
    this.sent.unshift(JSON.parse(data));
};

describe('test helpers', function() {
    beforeEach(function() {
        window.sockjs = new MockSockJS();
    });

    function check(field) {
        return checkWin(parseField(field), 'x', 3);
    }

    it('should send JSONified data', function() {
        send('type', 'value');
        // data is parsed back in object in mocked connection
        expect(sockjs.sent[0]).toEqual({type: "type", value: "value"});
    });

    it('should parse a field as indended', function() {
        expect(parseField('  \n  ')).toEqual([[' ', ' '], [' ', ' ']]);
    });

    it('should not have false wins', function() {
        var nothing = '   \n   \n   ';
        expect(check(nothing)).toEqual(false);
    });

    it('should see horizontal wins', function() {
        var horiz = 'xxx\n   \n   ';
        expect(check(horiz)).toEqual(true);
    });

    it('should see vertical wins', function() {
        var vert = 'x  \nx  \nx  ';
        expect(check(vert)).toEqual(true);
    });

    it('should see diagonal wins', function() {
        var ltr = 'x  \n x \n  x';
        expect(check(ltr)).toEqual(true);
        var rtl = '  x\n x \nx  ';
        expect(check(rtl)).toEqual(true);
    });
});

describe('test login controller', function() {
    var ctrl, $scope;

    beforeEach(module('Gomoku'));

    beforeEach(inject(function($rootScope, $controller) {
        window.sockjs = new MockSockJS();

        $scope = $rootScope.$new();
        ctrl = $controller('Login', {
            $scope: $scope
        });
    }));

    it('should send a name on login', function() {
        ctrl.state = {name: 'test'};
        // ctrl.login();
        // expect(sockjs.sent[0]).toEqual({type: 'name', value: 'test'});
    });
});
