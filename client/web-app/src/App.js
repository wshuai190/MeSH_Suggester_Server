import { React, useState } from "react";
import TextField from "@mui/material/TextField";
import TextareaAutosize from '@mui/material/TextareaAutosize';
import Box from '@mui/material/Box';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import SearchIcon from '@mui/icons-material/Search';
import Alert from '@mui/material/Alert';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import "./App.css";


function App() {
    const [term, setTerm] = useState("");
    const [type, setType] = useState("Semantic");
    const [data, setData] = useState({"Splits": [], "Data": []})
    const [textArea, setTextArea] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [err, setErr] = useState('');


    const handleChange = event => {
        setTerm(event.target.value);
    }

    const handleRadioChange = event => {
        setType(event.target.value);
    }

    const handleAddButton = event => {
        let tmp = textArea + " OR " + event.target.value + "[MeSH]"
        setTextArea(tmp);
    }

    const textChange = event => {
        setTextArea(event.target.value);
    }

    const handleClick = async () => {
        setIsLoading(true);
        setErr('');

        // const uri = 'https://ede9-130-102-10-104.au.ngrok.io/api/v1/resources/mesh?term=' + term + '&type=' + type;
        const uri = 'http://127.0.0.1:5000/api/v1/resources/mesh?term=' + term + '&type=' + type;

        try {
            const response = await fetch(uri, {
                method: "GET",
                headers: {
                    Accept: "application/json",
                },
                mode: 'cors'
            });


            if (!response.ok) {
                throw new Error(`Error! Status: ${response.status}`);
            }

            const result = await response.json();

            setData(result);
	    if (textArea === "") {
		setTextArea(result['Splits'].map((keyword) => `${keyword + "[tiab]"}`).join(' OR '))    
	    }
        } catch (err) {
            setErr(err.message);
        } finally {
            setIsLoading(false);
        }

    };

    return (
        <div className="main">
            <h1>MeSH Term Suggestion Tool</h1>
            <div className="search">
                <Box component="div" display="inline">
                    <TextField
                        id="outlined-basic"
                        variant="outlined"
                        name="text"
                        onChange={handleChange}
                        value={term}
                        autoComplete="off"
                        fullWidth
                        label="Input Keywords Separated By $ Sign"
                    />
                </Box>
            </div>

            <FormControl>
                <RadioGroup
                    row
                    aria-labelledby="demo-row-radio-buttons-group-label"
                    name="row-radio-buttons-group"
                    value={type}
                    onChange={handleRadioChange}
                >
                    <FormControlLabel value="Semantic" control={<Radio />} label="Semantic-BERT" />
                    <FormControlLabel value="Fragment" control={<Radio />} label="Fragment-BERT" />
                    <FormControlLabel value="Atomic" control={<Radio />} label="Atomic-BERT" />
                    <FormControlLabel value="ATM" control={<Radio />} label="ATM" />
                    <FormControlLabel value="MetaMap" control={<Radio />} label="MetaMap" />
                    <FormControlLabel value="UMLS" control={<Radio />} label="UMLS" />
                </RadioGroup>
            </FormControl>

            {err && <Alert severity="error">{err}</Alert>}

            {isLoading ? (
                <Box component="div" display="inline">
                    <LoadingButton loading
                                   loadingPosition="start"
                                   startIcon={<SearchIcon />}
                                   variant="contained" onClick={handleClick} >Suggest</LoadingButton>
                </Box>
            ) : (
                <Box component="div" display="inline">
                    <LoadingButton
                                   loadingPosition="start"
                                   startIcon={<SearchIcon />}
                                   variant="contained" onClick={handleClick} >Suggest</LoadingButton>
                </Box>
            )}

            <TextareaAutosize
                aria-label="query-formulate"
                minRows={5}
                placeholder="Formulate Your Query Here"
                style={{ width: 700, minHeight: 80, maxHeight: 80 }}
                value={textArea}
                onChange={textChange}
            />

            <div className="accord">
                {data['Data'].map((mesh, index) => {
                    return (
                        <Accordion key={index} >
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon />}
                                aria-controls={"panel"+(index+1)+"a-content"}
                                id={"panel"+(index+1)+"a-header"}
                            >
                                <Typography>Keyword: {mesh.Keywords.map((keyword) => `${keyword}`).join(', ')}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Typography>MeSH Terms:</Typography>
                                <ul>
                                    {
                                        Object.entries(mesh.MeSH_Terms)
                                            .map(([key, value]) => <li key={key}><Typography key={key}><Button variant="contained" color="primary" size="small" onClick={handleAddButton} key={key} value={value}>ADD</Button> {key}: {value}</Typography></li>)
                                    }
                                </ul>
                            </AccordionDetails>
                        </Accordion>
                    )
                })
                }
            </div>
        </div>
    );
}
export default App;
