
var mapf = function () {
            value = {}
            value[this.v[0]] = {}
            value[this.v[0]][this.v[1]] = this.v[2]
            emit(JSON.stringify(this.l), {'l': this.l, 'v': value});
          }

var reducef = function (l, docs) {
                values = {};
                docs.forEach(function (doc) {
                    Object.keys(doc.v).forEach(function (day) {
                        values[day] = Object.assign(values[day] || {}, doc.v[day]);
                    });
                });
                return {'l': l, 'v': values};
            }

db.runCommand(
               {
                 mapReduce: 'tide_insert',
                 map: mapf,
                 reduce: reducef,
                 out: 'mapreduce',
               }
             )