run: init
	echo python -m snewpdag # needs config and input JSON filenames

lightcurvesim:
	cd externals/lightcurve_match && make simulation
	cd externals/lightcurve_match/matching && make getdelay

standalone_unittests:
	python -m unittest snewpdag.tests.test_basic_node
	python -m unittest snewpdag.tests.test_app
	python -m unittest snewpdag.tests.test_inputs
	python -m unittest snewpdag.tests.test_combinemaps

test: standalone_unittests lightcurvesim
	python -m unittest snewpdag.tests.test_timedistdiff

runtest:
	python -m snewpdag \
          --input snewpdag/data/test-flux-input.json \
          snewpdag/data/test-flux-config.json

histogram:
	python snewpdag/trials/Normal.py hist --expt Newt | \
          python -m snewpdag --jsonlines \
          snewpdag/data/test-dags-hist-config.json

trial:
	python snewpdag/trials/Simple.py Control -n 10 > my_json_structure_test.txt
#| \
          python -m snewpdag --jsonlines snewpdag/data/test-gen-config.py


trial2:
	python -m snewpdag --stream STREAM --log INFO --jsonlines snewpdag/data/test-liq-config.py #python #snewpdag/trials/sub.py --stream STREAM --log INFO --jsonlines snewpdag/data/test-liq-config.py #--input /home/riccardo/Documents/GitHub/snewpdag/SNEWS_MSGs/subscribed_messages_test.json --log INFO --jsonlines snewpdag/data/test-liq-config.py #|  \
          #python -m snewpdag --log INFO --jsonlines snewpdag/data/test-liq-config.py



#trial2:
#	python snewpdag/trials/Simple.py Control -n 1 | \
#          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-liq-config.py

diffpointing:
	python snewpdag/trials/Simple.py Control -n 1 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-diff.py

distcalc_trial:
	python snewpdag/trials/Simple.py Control -n 1000 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-distcalc-single-config.csv

distcalc_err_trial:
	python snewpdag/trials/Simple.py Control -n 5000 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-distcalc-err-config.csv

init:
	pip install -r requirements.txt

.PHONY: init run test histogram trial trial2 runtest
