import logging
import requests
from urlparse import urljoin
from lxml import html
from normality import slugify, collapse_spaces, stringify
from itertools import count

from libsanctions import Source, Entity, make_uid

log = logging.getLogger(__name__)
SEXES = {
    'Male': Entity.GENDER_MALE,
    'Female': Entity.GENDER_FEMALE,
}


def element_text(el):
    if el is None:
        return
    text = stringify(unicode(el.text_content()))
    if text is not None:
        return collapse_spaces(text)


def scrape_case(source, url):
    res = requests.get(url)
    doc = html.fromstring(res.content)
    name = element_text(doc.find('.//div[@class="nom_fugitif_wanted"]'))
    if name is None or name == 'Identity unknown':
        return
    uid = make_uid(url)
    entity = source.create_entity(uid)
    entity.url = url
    entity.type = entity.TYPE_INDIVIDUAL
    entity.name = name
    entity.program = element_text(doc.find('.//span[@class="nom_fugitif_wanted_small"]'))  # noqa

    if ', ' in name:
        last, first = name.split(', ', 1)
        alias = entity.create_alias()
        alias.name = ' '.join((first, last))

    dob, pob = None, None
    for row in doc.findall('.//div[@class="bloc_detail"]//tr'):
        title, value = row.findall('./td')
        name = slugify(element_text(title), sep='_')
        value = element_text(value)
        if value is None:
            continue
        if name == 'charges':
            entity.summary = value
        elif name == 'present_family_name':
            entity.last_name = value
        elif name == 'forename':
            entity.first_name = value
        elif name == 'nationality':
            for country in value.split(', '):
                nationality = entity.create_nationality()
                nationality.country = country
        elif name == 'sex':
            entity.gender = SEXES[value]
        elif name == 'date_of_birth':
            dob = value.split('(')[0]
        elif name == 'place_of_birth':
            pob = value
        # else:
        #     print name

    if dob is not None or pob is not None:
        birth = entity.create_birth()
        birth.date = dob
        birth.place = pob
    entity.save()


def scrape():
    url = 'http://www.interpol.int/notice/search/wanted/(offset)/%s'
    source = Source('interpol-red-notices')
    seen = set()
    for i in count(0):
        p = i * 9
        res = requests.get(url % p)
        doc = html.fromstring(res.content)
        links = doc.findall('.//div[@class="wanted"]//a')
        if not len(links):
            break
        for link in links:
            case_url = urljoin(url, link.get('href'))
            if case_url in seen:
                continue
            seen.add(case_url)
            scrape_case(source, case_url)

    source.finish()


if __name__ == '__main__':
    scrape()
