FROM pudo/libsanctions
MAINTAINER Friedrich Lindenberg <friedrich@pudo.org>

COPY . /scraper
WORKDIR /scraper
# RUN pip install -q -r requirements.txt
CMD python scraper.py
