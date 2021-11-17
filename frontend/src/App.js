import './App.css';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import * as React from 'react';
import client from "./client";
import {Typography} from "@mui/material";
import {
    Pause as PauseIcon,
    PlayArrow as PlayArrowIcon,
    SkipNext as SkipNextIcon,
    SkipPrevious as SkipPreviousIcon,
    Sync as SyncIcon,
    WbSunny as SunnyIcon,
    Radio as RadioIcon
} from '@mui/icons-material';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {playing: "Loading...", time_left: 0};
        this.checkPlaying = this.checkPlaying.bind(this);
    }

    componentDidMount() {
        this.checkPlaying();
    }

    checkPlaying() {
        //console.log("check")
        client.get("playing").then(res => {
            console.log(res)
            this.setState({
                ...res.data
            });
            clearTimeout(this.update)
            //if (res.data.time_left > 0) {
            this.update = setTimeout(this.checkPlaying, 1000);//res.data.time_left);
            //}
        })
    }

    render() {
        return <React.Fragment>
            <CssBaseline/>
            <div className={"main"}>
                <Typography>{this.state.playing}</Typography>
                {
                    (this.state.time_left < 0)
                    && <Typography>Paused</Typography>
                    || <Typography>Next track in {Math.round(this.state.time_left / 1000)} seconds</Typography>
                }
                <br/>
                <Button
                    variant="contained"
                    startIcon={<SyncIcon/>}
                    onClick={() => this.checkPlaying()}
                >Sync</Button>
                <br/>
                <br/>
                <Button
                    variant="contained"
                    startIcon={<SkipPreviousIcon/>}
                    onClick={() => client.post("back").then(() => this.checkPlaying())}
                >Back</Button>
                <Button
                    variant="contained"
                    startIcon={<SkipNextIcon/>}
                    onClick={() => client.post("next").then(() => this.checkPlaying())}
                >Next</Button>
                <br/>
                <br/>
                {
                    (this.state.time_left < 0)
                    && <Button
                        variant="contained"
                        startIcon={<PlayArrowIcon/>}
                        onClick={() => client.post("unpause").then(() => this.checkPlaying())}
                    >Unpause</Button>
                    || <Button
                        variant="contained"
                        startIcon={<PauseIcon/>}
                        onClick={() => client.post("pause").then(() => this.checkPlaying())}
                    >Pause</Button>
                }
                <br/>
                <br/>
                <Button
                    variant="contained"
                    startIcon={<SunnyIcon/>}
                    onClick={() => client.post("weather").then(() => this.checkPlaying())}
                >Weather</Button>
                <br/>
                <br/>
                <Button
                    variant="contained"
                    startIcon={<RadioIcon/>}
                    onClick={() => client.post("break").then(() => this.checkPlaying())}
                >Break</Button>
            </div>
        </React.Fragment>
            ;
        /*return (
          <div className="App">
            <header className="App-header">
              <img src={logo} className="App-logo" alt="logo" />
              <p>
                Edit <code>src/App.js</code> and save to reload.
              </p>
              <a
                className="App-link"
                href="https://reactjs.org"
                target="_blank"
                rel="noopener noreferrer"
              >
                Learn React
              </a>
            </header>
          </div>
        );*/
    }
}

export default App;
