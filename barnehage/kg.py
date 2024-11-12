from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from numpy import integer

from barnehage.dbexcel import soknad
from barnehage.kgcontroller import select_barnehage_by_id
from kgcontroller import select_alle_soknader
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad,
                          insert_soknad,
                          commit_all,
                          select_alle_barnehager)

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        print(sd)
        log = insert_soknad(form_to_object_soknad(sd))
        print(log)
        session['information'] = sd
        return redirect(url_for('svar')) #[1]
    else:
        return render_template('soknad.html')

@app.route('/svar')
def svar():

    information = session['information']
    priorities = information['liste_over_barnehager_prioritert_5']
    barnehage_liste = []
    message = ""
    if len(priorities) > 0:
        try:
            kgpr = priorities.split(',')
            for kgid in kgpr:
                kg_instance = select_barnehage_by_id(int(kgid), select_alle_barnehager())
                if kg_instance[0].barnehage_ledige_plasser != 0:
                    barnehage_liste.append(kg_instance[0])
            if len(barnehage_liste) != 0:
                message = "Tilbud"
            else:
                message = "Avslag"
        except ValueError:
            message = "Forbidden value"
            return render_template('svar-error.html',message=message)
        except IndexError:
            message = "Contains value outside index"
            return render_template('svar-error.html',message=message)
    else:
        message = "Ingen barnehager valgt"
    print(barnehage_liste)
    return render_template('svar.html', data=information, kglist = barnehage_liste, message=message)


@app.route('/commit')
def commit():
    commit_all()
    return render_template('commit.html')

@app.route('/soknader')
def soknader():
    soknader = select_alle_soknader()
    status = ["avslag", "tilbud"]

    return render_template('soknader.html', soknader=soknader, status=status, len=len(soknader))




"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""