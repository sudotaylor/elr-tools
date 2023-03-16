from lxml import etree

class Person:
    id: str = ""
    fname: str = ""
    mname: str = ""
    lname: str = ""
    birthDate: str = ""
    gender: str = ""
    race: str = ""
    ethnicity: str = ""
    pLanguage: str = ""
    isDead: bool = False
    deathDate: str = ""
    telecomList: list[str] = []
    phones: str = ""
    emails: str = ""
    def updateTelecom(self) -> None:
        phones: list[str] = []
        emails: list[str] = []
        for telecom in self.telecomList:
            if telecom.startswith("tel:"):
                phones.append(telecom[4:])
            elif telecom.startswith("mailto:"):
                emails.append(telecom[7:])
        self.phones = ", ".join(phones)
        self.emails = ", ".join(emails)
    def toStringHeaders(self) -> str:
        return("\t".join(["ID", "First Name", "Middle Name", "Last Name", "Date of Birth", "Gender", "Race", "Ethnicity", "Preferred Language", "isDead?", "Date of Death", "Telecom List", "Phone(s)", "Email(s)"]))
    def toString(self) -> str:
        return("\t".join([self.id, self.fname, self.mname, self.lname, self.birthDate, self.gender, self.race, self.ethnicity, self.pLanguage, self.isDead, self.deathDate, str(self.telecomList), self.phones, self.emails]))

def extractXmlPatient(record: etree._Element) -> Person:
    p: Person = Person()

    class Attr:
        numArgs: int = 0
        attribName: str = ""
        path: any = ""
        def update(self, numArgs: int, attribName: str, path: any):
            self.numArgs = numArgs
            self.attribName = attribName
            self.path = path
            return self
    
    attributes: list[Attr] = [
        Attr().update(
            1, 'id', record.xpath('./recordTarget/patientRole/id[1]/@extension')
        ),
        Attr().update(
            1, 'fname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[1]/text()')
        ),
        Attr().update(
            1, 'mname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/given[2]/text()')
        ),
        Attr().update(
            1, 'lname', record.xpath('./recordTarget/patientRole/patient/name[@use="L"]/family/text()')
        ),
        Attr().update(
            1, 'birthDate', record.xpath('./recordTarget/patientRole/patient/birthTime/@value')
        ),
        Attr().update(
            1, 'gender', record.xpath('./recordTarget/patientRole/patient/administrativeGenderCode/@displayName')
        ),
        Attr().update(
            1, 'race', record.xpath('./recordTarget/patientRole/patient/raceCode[1]/@displayName')
        ),
        Attr().update(
            1, 'ethnicity', record.xpath('./recordTarget/patientRole/patient/ethnicGroupCode/@displayName')
        ),
        Attr().update(
            1, 'pLanguage', record.xpath('./recordTarget/patientRole/patient/languageCommunication/languageCode/@code')
        ),
        Attr().update(
            1, 'isDead', record.xpath('./recordTarget/patientRole/patient/deceasedInd/@value')
        ),
        Attr().update(
            1, 'deathDate', record.xpath('./recordTarget/patientRole/patient/deceasedTime/@value')
        ),
        Attr().update(
            -1, 'telecomList', record.xpath('./recordTarget/patientRole/telecom/@value')
        )
    ]

    for a in attributes:
        if a.path != None:
            if len(a.path) == a.numArgs:
                if a.numArgs == 1:
                    p.__setattr__(a.attribName, a.path[0])
                elif a.numArgs > 1: ## multiple args, comma-seperated (can change to list if needed)
                    p.__setattr__(a.attribName, ", ".join(a.path))
                else:
                    print(f"Error: Invalid number of arguments in {a.attribName}. Expected {a.numArgs}, but this is not a valid option - check the configuration.") ## should never occur
            elif a.numArgs == -1: ## add as list
                p.__setattr__(a.attribName, a.path)
            elif len(a.path) == 0:
                pass ## empty - may not be required - use validation to check
            else:
                print(f"Error: Incorrect number of arguments in {a.attribName}. Expected {a.numArgs}, but found {len(a.path)}.")
    p.updateTelecom()

    ## Validation
    ## ...

    return p


xmlFiles:list[str] = ["ecr_example1.xml"]


for xmlFile in xmlFiles:
    xmltree: etree._ElementTree = etree.parse(xmlFile)
    root: etree._Element = xmltree.getroot()
    #namespace = root.tag[1:].split("}")[0] ## in case capturing namespace is important
    #for record in root.findall('{' + namespace + '}title'):
    #    print(record.text) ## or, you know, do something more useful
    ## (strip all namespaces):
    for element in root.getiterator():
        if not (isinstance(element, etree._Comment) or isinstance(element, etree._ProcessingInstruction)):
            element.tag = etree.QName(element).localname
    etree.cleanup_namespaces(root)
    
    with open('output.tsv', 'w') as f:
        f.write(Person().toStringHeaders() + '\n')
        f.write(extractXmlPatient(root).toString() + '\n')
