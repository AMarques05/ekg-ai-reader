import Button from './Button';
import Input from './Input';
import Result from './Result';

function InfoContainer(){
    return(
        <div className = "flex flex-col justify-center items-center row-span-2 px-1 py-2 gap-y-2">
            <h1 className = "text-white font-mono text-2xl antialiased font-bold">EKG-AI-Reader</h1>
              <Input />
              <Button />
              <Result />
        </div>
    )
}

export default InfoContainer;