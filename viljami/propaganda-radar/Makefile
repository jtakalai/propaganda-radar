.PHONY: feed watch dashboard clean

feed:
	python3 feeder.py

watch:
	python3 feeder.py --interval 900

dashboard:
	streamlit run dashboard.py

clean:
	rm -rf __pycache__
