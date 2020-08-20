from setup import config
if(config['archiveTalk']['status']):
    import archive
    archive()
if(config["reduceImage"]['status']):
    import reduceImage
    reduceFUR()
if(config["goodArticle"]["status"]):
    import ga
    manageGATalk()
    manageGAR()
    if(config["goodArticle"]["manageNominee"]["status"]):
        config = config["goodArticle"]["manageNominee"]
        manageNominee()